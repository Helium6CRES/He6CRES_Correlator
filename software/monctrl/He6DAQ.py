#!/usr/bin/env python

import adc5g
from copy import deepcopy
from corr.katcp_wrapper import FpgaClient
from datetime import datetime
import netifaces as ni
from numpy import (
	abs,
	array,
	ceil,
	complex64,
	concatenate,
	float32,
	floor,
	int8,
	pi,
	uint32,
	uint64,
	uint8,
	zeros,
	)
from scipy.signal import firwin2
from socket import socket, AF_INET, SOCK_DGRAM
from struct import unpack
from time import sleep, time

class Packet():
	"""
	Encapsulate an He6CRES packet. Header length and structure are retained from R2DAQ (aka ArtooDaq)
	"""

	BYTES_IN_PAYLOAD = 8192
	BYTES_IN_HEADER = 32
	BYTES_IN_PACKET = BYTES_IN_PAYLOAD + BYTES_IN_HEADER

	@property
	def unix_time(self):
		return self._unix_time

	@property
	def pkt_in_batch(self):
		return self._pkt_in_batch

	@property
	def digital_id(self):
		return self._digital_id

	@property
	def if_id(self):
		return self._if_id

	@property
	def user_data_1(self):
		return self._user_data_1

	@property
	def user_data_0(self):
		return self._user_data_0

	@property
	def reserved_0(self):
		return self._reserved_0

	@property
	def reserverd_1(self):
		return self._reserved_1

	@property
	def freq_not_time(self):
		return self._freq_not_time

	@property
	def data(self):
		return self._data

	def __init__(self,ut=0,pktnum=0,did=0,ifid=0,ud0=0,ud1=0,res0=0,res1=0,fnt=False,data=None):
		"""
		Initialize Packet with the given attributes
		"""
		# assign attributes
		self._unix_time = ut
		self._pkt_in_batch = pktnum
		self._digital_id = did
		self._if_id = ifid
		self._user_data_0 = ud0
		self._user_data_1 = ud1
		self._reserved_0 = res0
		self._reserved_1 = res1
		self._freq_not_time = fnt
		self._data = data

	def interpret_data(self):
		"""
		Returns
		-------
		x : ndarray
		    real-valued array represented by the data.
		"""
		x = array(self.data, dtype = uint16)
		return x

	@classmethod
	def FromByteString(cls,bytestr):
		"""
		Parse packet header and data from the given byte string, return an object of type Packet
		"""
		# check correct size packet
		len_bytes = len(bytestr)
		if not len_bytes == cls.BYTES_IN_PACKET:
			raise ValueError("Packet should comprise {0} bytes, but has {1} bytes".format(len_bytes,cls.BYTES_IN_PACKET))
		# unpack header
		hdr = unpack(">{0}Q".format(cls.BYTES_IN_HEADER/8),bytestr[:cls.BYTES_IN_HEADER])
		ut = uint32(hdr[0] & 0xFFFFFFFF)
		pktnum = uint32((hdr[0]>>uint32(32)) & 0xFFFFF)
		did = uint8(hdr[0]>>uint32(52) & 0x3F)
		ifid = uint8(hdr[0]>>uint32(58) & 0x3F)
		ud1 = uint32(hdr[1] & 0xFFFFFFFF)
		ud0 = uint32((hdr[1]>>uint32(32)) & 0xFFFFFFFF)
		res0 = uint64(hdr[2])
		res1 = uint64(hdr[3]&0x7FFFFFFFFFFFFFFF)
		fnt = not (hdr[3]&0x8000000000000000 == 0)
		# unpack data in 64bit mode to correct for byte-order
		data_64bit = array(unpack(">{0}Q".format(cls.BYTES_IN_PAYLOAD/8),bytestr[cls.BYTES_IN_HEADER:]),dtype=uint64)
		data = zeros(cls.BYTES_IN_PAYLOAD,dtype=int8)
		for ii in xrange(len(data_64bit)):
			for jj in xrange(8):
				data[ii*8+jj] = int8((data_64bit[ii]>>uint64(8*jj))&uint64(0xFF))
		return Packet(ut,pktnum,did,ifid,ud0,ud1,res0,res1,fnt,data)

class He6CRES_DAQ(object):
	"""
	Encapsulate a DAQ object. Based on the R2DAQ (aka ArtooDaq) class from Andre Young.
	"""

	_TIMEOUT = 5
	_FPGA_CLOCK = 200e6
	_DEMUX = 16
	_ADC_SAMPLE_RATE = _FPGA_CLOCK * _DEMUX
	_CHANNEL_WIDTH = 1000e6

	_PHASE_LOOKUP_DEPTH = 10

	@property
	def FPGA_CLOCK(self):
		return self._FPGA_CLOCK

	@property
	def DEMUX(self):
		return self._DEMUX

	@property
	def ADC_SAMPLE_RATE(self):
		return self._ADC_SAMPLE_RATE

	@property
	def CHANNEL_WIDTH(self):
		return self._CHANNEL_WIDTH

	@property

	def PHASE_LOOKUP_DEPTH(self):
		return self._PHASE_LOOKUP_DEPTH

	@property
	def registers(self):
		registers = dict()
		for k in self.roach2.listdev():
			registers[k] = self.roach2.read_int(k)
		return registers

	@property
	def roach2(self):
		return self._roach2

	@property
	def version(self):
		reg = self.registers
		return (reg['rcs_lib'],reg['rcs_app'],reg['rcs_user'])

	def print_version(self,ver=None):
		"""
		Print detailed bitcode version information.

		Parameters
		----------
		ver : tuple
		    The version tuple to interpret, as returned by the
		    ArtooDaq.version property. If None, then the tuple is first
		    obtained from the current ArtooDaq instance. Default is None.
		"""
		def _app_or_lib_to_str(v):
			b31_format = ('revision system','timestamp')
			_FORMAT_REVISION = 0
			_FORMAT_TIMESTAMP = 1

			b30_rtype = ('git','svn')
			_RTYPE_GIT = 0
			_RTYPE_SVN = 1

			b28_dirty = ('all changes in revision control','changes not in revision control')
			_DIRTY_SAVED = 0
			_DRITY_UNSAVED = 1

			str_out = ''
			v_format = (v & 0x80000000) >> 31
			str_out = '   Format: {0}'.format(b31_format[v_format])
			if v_format == _FORMAT_REVISION:
				v_rtype = (v & 0x40000000) >> 30
				str_out = '\n'.join([str_out,'     Type: {0}'.format(
					b30_rtype[v_rtype]
				)])
				v_dirty = (v & 0x10000000) >> 28
				str_out = '\n'.join([str_out,'    Dirty: {0}'.format(
					b28_dirty[v_dirty]
				)])
				if v_rtype == _RTYPE_GIT:
					v_hash = (v & 0x0FFFFFFF)
					str_out = '\n'.join([str_out,'     Hash: {0:07x}'.format(
						v_hash
					)])
				else:
					v_rev = (v & 0x0FFFFFFF)
					str_out = '\n'.join([str_out,'      Rev: {0:9d}'.format(
						v_rev
					)])
			else:
				v_timestamp = (v & 0x3FFFFFFF)
				str_out = '\n'.join([str_out,'     Time: {0}'.format(
					datetime.fromtimestamp(float(v_timestamp)).strftime("%F %T")
				)])
			return str_out

		if ver is None:
			ver = self.version
		vl,va,vu = ver
		str_out = 'CASPER Library'
		str_out = '\n'.join([str_out,'=============='])
		str_out = '\n'.join([str_out,_app_or_lib_to_str(vl)])
		str_out = '\n'.join([str_out,'Application'])
		str_out = '\n'.join([str_out,'==========='])
		str_out = '\n'.join([str_out,_app_or_lib_to_str(va)])
		str_out = '\n'.join([str_out,'User'])
		str_out = '\n'.join([str_out,'===='])
		str_out = '\n'.join([str_out,'  Version: {0:10d}'.format(vu)])
		print str_out

	def __init__(self,hostname,dsoc_desc=None,boffile=None):
		"""
		Initialize an ArtooDaq object.

		Parameters
		----------
		hostname : string
		    Address of the roach2 on the 1GbE (control) network.
		dsoc_desc : tuple
		    A tuple with the first element the IP address / hostname and
		    the second element the port where data is to be received. This
		    argument, if not None, is passed directly to socket.bind(); see
		    the documentation of that class for details. In this case a
		    socket is opened and bound to the given address. If None, then
		    the data socket is not opened. Default is None.
		boffile : string
		    Program the device with this bitcode if not None. The special
		    filename 'latest-build' uses the current build of the bit-code.
		    Default is None.
		"""
		# connect to roach and store local copy of FpgaClient
		r2 = FpgaClient(hostname)
		if not r2.wait_connected(self._TIMEOUT):
			raise RuntimeError("Unable to connect to ROACH2 named '{0}'".format(hostname))
		self._roach2 = r2
		# program bitcode
		if not boffile is None:
			self._start(boffile)
		# if requested, open data socket
		if not dsoc_desc is None:
			self.open_dsoc(dsoc_desc)

	def grab_packets(self,n=1,dsoc_desc=None,close_soc=False):
		"""
		Grab packets using open data socket.

		Calls to this method should only be made while a data socket is
		open, unless a socket descriptor is provided. See open_dsoc() for
		details.

		Parameters
		----------
		n : int
		    Number of packets to grab, default is 1.
		dsoc_desc : tuple
		    Socket descriptor tuple as for open_dsoc() method. If None,
		    a data socket should already be open. Default is None.
		close_soc : boolean
		    Close socket after grabbing the given number of packets.
		"""
		if not dsoc_desc is None:
			self.open_dsoc(dsoc_desc)
		try:
			dsoc = self._data_socket
		except AttributeError:
			raise RuntimeError("No open data socket. Call open_dsoc() first.")
		pkts = []
		for ii in xrange(n):
			data = dsoc.recv(Packet.BYTES_IN_PACKET)
			pkts.append(Packet.FromByteString(data))
		if close_soc:
			self.close_dsoc()
		return pkts

	def open_dsoc(self,dsoc_desc):
		"""
		Open socket for data reception and bind.

		Parameters
		----------
		dsoc_desc: tuple
		    Tuple of IP address / hostname and port as passed to socket.bind().
		"""
		self._data_socket = socket(AF_INET,SOCK_DGRAM)
		self._data_socket.bind(dsoc_desc)
		return self._data_socket

	def close_dsoc(self):
		"""
		Close socket used for data reception.
		"""
		self._data_socket.close()


	def set_fft_shift(self,shift_vec='1010101010101',tag='ab'):
		"""
		Set shift vector for FFT engine.

		Parameters
		----------
		shift_vec : string
		    String given in bit-format, '1's and '0's where 1 indicates
		    right-shift at stage associated with the bit position. Only
		    the first 13 characters in the string are used. Default  is
		    '1101010101010' which ensures no overflow.
		tag : string
		    Tag selects the FFT engine to which the shift-vector is
		    applied. Default is 'ab'.
		"""
		self._check_valid_fft_engine(tag)
		idx = self.FFT_ENGINES.index(tag)
		regname = 'fft_ctrl'
		s_13bit = int(shift_vec,2) & 0x1FFF
		masked_val = self.registers[regname] & uint32(~(0x1FFF<<idx*13))
		self._make_assignment({regname: masked_val | uint32(s_13bit<<(idx*13))})

	def calibrate_adc_ogp(self,zdok,oiter=10,otol=0.005,giter=10,gtol=0.005,piter=0,ptol=1.0,verbose=10):
		"""
		Attempt to match the cores within the ADC.

		Each of the four cores internal to each ADC has an offset, gain,
		phase, and a number of integrated non-linearity parameters that
		can be independently tuned. This method attempts to match the
		cores within the specified ADC by tuning a subset of these
		parameters.

		Parameters
		----------
		zdok : int
			ZDOK slot that contains the ADC, should be 0 (default is 0).
			(Second ADC card introduced to He6CRES bitcode)
		oiter : int
			Maximum number of iterations to fine-tune offset parameter (default
			is 10).
		otol : float
			If the absolute value of the mean of snapshot data normalized to
			the standard deviation from one core is below this value then the
			offset-tuning is considered sufficient (default is 0.005).
		giter : int
			Maximum number of iterations to fine-tune gain parameter (default
			is 10).
		gtol : float
			If the distance between the standard deviation of the data in one
			core is less than this fraction of the standard deviation in the data
			from core1, then the gain-tuning is considered sufficient (default
			value is 0.005).
		piter : int
			Phase calibration not yet implemented.
		ptol : float
			Phase calibration not yet implemented.
		verbose : int
			The higher the more verbose, control the amount of output to
			the screen. Default is 10 (probably the highest).

		Returns
		-------
		ogp : dict
		    The returned parameter is a dictionary that contains the optimal
		    settings for offset, gain and phase as solved during calibration.
		"""
		if verbose > 3:
			print "Attempting OGP-calibration for ZDOK{0}".format(zdok)
		co = self.calibrate_adc_offset(zdok=zdok,oiter=oiter,otol=otol,verbose=verbose)
		cg = self.calibrate_adc_gain(zdok=zdok,giter=giter,gtol=gtol,verbose=verbose)
		cp = self.calibrate_adc_phase(zdok=zdok,piter=piter,ptol=ptol,verbose=verbose)
		return {'offset': co, 'gain': cg, 'phase': cp}

	def calibrate_adc_offset(self,zdok,oiter=10,otol=0.005,verbose=10):
		"""
		Attempt to match the core offsets within the ADC.

		See ArtooDaq.calibrate_adc_ogp for more details.
		"""
		# offset controlled by float varying over [-50,50] mV with 0.4 mV resolution
		res_offset = 0.4
		lim_offset = [-50.0,50.0]
		groups = 8
		test_step = 10*res_offset
		if verbose > 3:
			print "  Offset calibration ZDOK{0}:".format(zdok)
		for ic in xrange(1,5):
			adc5g.set_spi_offset(self.roach2,zdok,ic,0)
		x1 = self._snap_per_core(zdok=zdok,groups=groups)
		sx1 = x1.std(axis=0)
		mx1 = x1.mean(axis=0)/sx1
		if verbose > 5:
			print "    ...offset: with zero-offsets, means are [{0}]".format(
				", ".join(["{0:+7.4f}".format(imx) for imx in mx1])
			)
		for ic in xrange(1,5):
			adc5g.set_spi_offset(self.roach2,zdok,ic,test_step)
		x2 = self._snap_per_core(zdok=zdok,groups=groups)
		sx2 = x2.std(axis=0)
		mx2 = x2.mean(axis=0)/sx2
		if verbose > 5:
			print "    ...offset: with {0:+4.1f} mV offset, means are [{1}]".format(
				test_step,
				", ".join(["{0:+7.4f}".format(imx) for imx in mx2])
			)
		d_mx = (mx2 - mx1)/test_step
		core_offsets = -mx1/d_mx
		for ic in xrange(1,5):
			adc5g.set_spi_offset(self.roach2,zdok,ic,core_offsets[ic-1])
			core_offsets[ic-1] = adc5g.get_spi_offset(self.roach2,zdok,ic)
		x = self._snap_per_core(zdok=zdok,groups=groups)
		sx = x.std(axis=0)
		mx = x.mean(axis=0)/sx
		if verbose > 5:
			print "    ...offset: solution offsets are [{0}] mV, means are [{1}]".format(
				", ".join(["{0:+6.2f}".format(ico) for ico in core_offsets]),
				", ".join(["{0:+7.4f}".format(imx) for imx in mx])
			)
		if any(abs(mx) >= otol):
			if verbose > 5:
				print "    ...offset: solution not good enough, iterating (tol={0:4.4f},iter={1:d})".format(otol,oiter)
			for ii in xrange(0,oiter):
				for ic in xrange(1,5):
					if mx[ic-1] > otol:
						adc5g.set_spi_offset(self.roach2,zdok,ic,core_offsets[ic-1]-res_offset)
					elif mx[ic-1] < -otol:
						adc5g.set_spi_offset(self.roach2,zdok,ic,core_offsets[ic-1]+res_offset)
					core_offsets[ic-1] = adc5g.get_spi_offset(self.roach2,zdok,ic)
				x = self._snap_per_core(zdok=zdok,groups=groups)
				sx = x.std(axis=0)
				mx = x.mean(axis=0)/sx
				if verbose > 7:
					print "    ...offset: solution offsets are [{0}] mV, means are [{1}]".format(
						", ".join(["{0:+6.2f}".format(ico) for ico in core_offsets]),
        		        ", ".join(["{0:+7.4f}".format(imx) for imx in mx])
					)
				if all(abs(mx) < otol):
					if verbose > 5:
						print "    ...offset: solution good enough"
					break
				if ii==oiter-1:
					if verbose > 5:
						print "    ...offset: maximum number of iterations reached, aborting"
		else:
			if verbose > 5:
				print "    ...offset: solution good enough"
		return core_offsets

	def calibrate_adc_gain(self,zdok,giter=10,gtol=0.005,verbose=10):
		"""
		Attempt to match the core gains within the ADC.

		See ArtooDaq.calibrate_adc_ogp for more details.
		"""
		# gain controlled by float varying over [-18%,18%] with 0.14% resolution
		res_gain = 0.14
		lim_gain = [-18.0,18.0]
		groups = 8
		test_step = 10*res_gain
		if verbose > 3:
			print "  Gain calibration ZDOK{0}:".format(zdok)
		for ic in xrange(1,5):
			adc5g.set_spi_gain(self.roach2,zdok,ic,0)
		x1 = self._snap_per_core(zdok=zdok,groups=groups)
		sx1 = x1.std(axis=0)
		s0 = sx1[0]
		sx1 = sx1/s0
		if verbose > 5:
			print "    ...gain: with zero-offsets, stds are                                    [{0}]".format(
				", ".join(["{0:+7.4f}".format(isx) for isx in sx1])
			)
		# only adjust gains for last three cores, core1 is the reference
		for ic in xrange(2,5):
			adc5g.set_spi_gain(self.roach2,zdok,ic,test_step)
		x2 = self._snap_per_core(zdok=zdok,groups=groups)
		sx2 = x2.std(axis=0)
		s0 = sx2[0]
		sx2 = sx2/s0
		if verbose > 5:
			print "    ...gain: with {0:+6.2f}% gain, stds are                                    [{1}]".format(
				test_step,
				", ".join(["{0:+7.4f}".format(isx) for isx in sx2])
			)
		d_sx = 100*(sx2 - sx1)/test_step
		# give differential for core1 a non-zero value, it won't be used anyway
		d_sx[0] = 1.0
		# gains are in units percentage
		core_gains = 100*(1.0-sx1)/d_sx
		# set core1 gain to zero
		core_gains[0] = 0
		for ic in xrange(2,5):
			adc5g.set_spi_gain(self.roach2,zdok,ic,core_gains[ic-1])
			core_gains[ic-1] = adc5g.get_spi_gain(self.roach2,zdok,ic)
		x = self._snap_per_core(zdok=zdok,groups=groups)
		sx = x.std(axis=0)
		s0 = sx[0]
		sx = sx/s0
		if verbose > 5:
			print "    ...gain: solution gains are [{0}]%, stds are [{1}]".format(
				", ".join(["{0:+6.2f}".format(ico) for ico in core_gains]),
				", ".join(["{0:+7.4f}".format(isx) for isx in sx])
			)
		if any(abs(1.0-sx) >= gtol):
			if verbose > 5:
				print "    ...gain: solution not good enough, iterating (tol={0:4.4f},iter={1:d})".format(gtol,giter)
			for ii in xrange(0,giter):
				for ic in xrange(2,5):
					if (1.0-sx[ic-1]) > gtol:
						adc5g.set_spi_gain(self.roach2,zdok,ic,core_gains[ic-1]+res_gain)
					elif (1.0-sx[ic-1]) < -gtol:
						adc5g.set_spi_gain(self.roach2,zdok,ic,core_gains[ic-1]-res_gain)
					core_gains[ic-1] = adc5g.get_spi_gain(self.roach2,zdok,ic)
				x = self._snap_per_core(zdok=zdok,groups=groups)
				sx = x.std(axis=0)
				s0 = sx[0]
				sx = sx/s0
				if verbose > 7:
					print "    ...gain: solution gains are [{0}]%, stds are [{1}]".format(
							", ".join(["{0:+6.2f}".format(ico) for ico in core_gains]),
        	                ", ".join(["{0:+7.4f}".format(isx) for isx in sx])
					)
				if all(abs(1.0-sx) < gtol):
					if verbose > 5:
						print "    ...gain: solution good enough"
					break
				if ii==giter-1:
					if verbose > 5:
						print "    ...gain: maximum number of iterations reached, aborting"
		else:
			if verbose > 5:
				print "    ...gain: solution good enough"
		return core_gains

	def calibrate_adc_phase(self,zdok,piter=0,ptol=1.0,verbose=10):
		"""
		Attempt to match the core phases within the ADC.

		See ArtooDaq.calibrate_adc_ogp for more details.
		"""
		# phase controlled by float varying over [-14,14] ps with 0.11 ps resolution
		res_phase = 0.11
		lim_phase = [-14.0,14.0]
		if verbose > 3:
			print "  Phase calibration ZDOK{0}:".format(zdok)
		core_phases = zeros(4)
		for ic in xrange(1,5):
			core_phases[ic-1] = adc5g.get_spi_phase(self.roach2,zdok,ic)
		if verbose > 5:
			print "    ...phase: tuning not implemented yet, phase parameters are [{0}]".format(
				", ".join(["{0:+06.2f}".format(icp) for icp in core_phases])
			)
		return core_phases

	def _snap_per_core(self,zdok,groups=1):
		"""
		Get a snapshot of 8-bit data per core from the ADC.

		Parameters
		----------
		zdok : int
			ID of the ADC ZDOK slot, either 0 or 1
		groups : int
			Each snapshot grabs groups*(2**16) samples per core
			(default value is groups=1, for 2**16=65536 samples).

		Returns
		-------
		x : ndarray
			A (groups*(2**16), 4)-shaped array in which data along the
			first dimension contains consecutive samples taken form the
			same core. The data is ordered such that the index along
			the second dimension matches core-indexing in the spi-
			family of functions used to tune the core parameters.
		"""
		x = zeros((0,4))
		for ig in xrange(groups):
			grab = self.roach2.snapshot_get('snap_{0}_snapshot'.format(zdok))
        	        x_ = array(unpack('%ib' %grab['length'], grab['data']))
                	x_ = x_.reshape((x_.size/4,4))
			x = concatenate((x,x_))
		return x[:,[0,2,1,3]]

	def _make_assignment(self,assign_dict):
		"""
		Assign values to ROACH2 software registers.

		Assignments are made as roach2.write_int(key,val).

		Parameters
		----------
		assign_dict : dict
		    Each key in assign_dict should correspond to a valid ROACH2
		    software register name, and each val should be int compatible.
		"""
		for key in assign_dict.keys():
			val = assign_dict[key]
			self.roach2.write_int(key,val)

	def _start(self,boffile='latest-build',do_cal=True,iface="p11p1",verbose=10):
		"""
		Program bitcode on device.

		Parameters
		----------
		boffile : string
		    Filename of the bitcode to program. If 'latest-build' then
		    use the current build. Default is 'latest-build'.
		do_cal : bool
		    If true then do ADC core calibration. Default is True.
		iface : string
		    Network interface connected to the data network.
		verbose : int
		    The higher the more verbose, control the amount of output to
		    the screen. Default is 10 (probably the highest).
		Returns
		-------
		"""

		if boffile == "latest-build":
			boffile = "he6_cres_correlator_2018_Sep_14_2002.bof"

		# program bitcode
		self.roach2.progdev(boffile)
		self.roach2.wait_connected()
		if verbose > 1:
			print "Bitcode '", boffile, "' programmed successfully"

		# display clock speed
		if verbose > 3:
			print "Board clock is ", self.roach2.est_brd_clk(), "MHz"

		# ADC interface calibration
		if verbose > 3:
			print "Performing ADC interface calibration... "
		adc5g.set_test_mode(self.roach2, 0)
		adc5g.set_test_mode(self.roach2, 1)
		adc5g.sync_adc(self.roach2)
		opt0, glitches0 = adc5g.calibrate_mmcm_phase(self.roach2, 0, ['snap_0_snapshot',])
		opt1, glitches1 = adc5g.calibrate_mmcm_phase(self.roach2, 1, ['zdok_1_snap_data',])
		adc5g.unset_test_mode(self.roach2, 0)
		adc5g.unset_test_mode(self.roach2, 1)
		if verbose > 3:
			print "...ADC interface calibration done."
		if verbose > 5:
			print "if0: opt0 = ",opt0, ", glitches0 = \n", array(glitches0)
			print "if1: ",opt0, glitches0

		# ADC core calibration
		if do_cal:
			self.calibrate_adc_ogp(zdok,verbose=verbose)

		# build channel-list
		ch_list = ['a','b','c','d','e','f','g','h']
		self._implemented_digital_channels = []
		for ch in ch_list:
			try:
				self.roach2.read_int("tengbe_{0}_ctrl".format(ch))
				self._implemented_digital_channels.append(ch)
			except RuntimeError:
				pass
		if verbose > 3:
			print "Valid channels in this build: {0}".format(self.implemented_digital_channels)


		# hold master reset signal and arm the manual sync
		self.roach2.write_int('master_ctrl',0x00000001 | 0x00000002)
		master_ctrl = self.roach2.read_int('master_ctrl')
		# hold 10gbe reset signal
		for ch in self.implemented_digital_channels:
			self.roach2.write_int('tengbe_{0}_ctrl'.format(ch),0x80000000)
		# ip, port of data interface on receive side
		dest_ip_str_cmp = ni.ifaddresses(iface)[2][0]['addr'].split('.')
		ip3 = int(dest_ip_str_cmp[0])
		ip2 = int(dest_ip_str_cmp[1])
		ip1 = int(dest_ip_str_cmp[2])
		ip0 = int(dest_ip_str_cmp[3])
		dest_ip = (ip3<<24) + (ip2<<16) + (ip1<<8) + ip0
		dest_port = 4001
		# fill arp table on ROACH2
		mac_iface = ni.ifaddresses(iface)[17][0]['addr']
		hex_iface = int(mac_iface.translate(None,':'),16)
		arp = [0xffffffffffff] * 256
		arp[ip0] = hex_iface
		# and configure
		ch_offset = 0
		for ch in self.implemented_digital_channels:
			# ip, port, mac of data interface on transmit side
			src_ip = (ip3<<24) + (ip2<<16) + (ip1<<8) + 2+ch_offset
			src_port = 4000
			src_mac = (2<<40) + (2<<32) + src_ip
			self.roach2.config_10gbe_core('tengbe_{0}_core'.format(ch),src_mac,src_ip,src_port,arp)
			self.roach2.write_int('tengbe_{0}_ip'.format(ch),dest_ip)
			self.roach2.write_int('tengbe_{0}_port'.format(ch),dest_port+ch_offset)
			ch_offset = ch_offset + 1
		# and release reset
		for ch in self.implemented_digital_channels:
			self.roach2.write_int('tengbe_{0}_ctrl'.format(ch),0x00000000)
		# set time, wait until just before a second boundary
		while(abs(datetime.utcnow().microsecond-9e5)>1e3):
			sleep(0.001)
		# when the system starts running it will be the next second
		ut0 = int(time())+1
		self.roach2.write_int('unix_time0',ut0)
		# release master reset signal
		master_ctrl = self.roach2.read_int('master_ctrl')
		master_ctrl = master_ctrl & 0xFFFFFFFC
		self.roach2.write_int('master_ctrl',master_ctrl)
		if verbose > 1:
			print "Configuration done, system should be running"
