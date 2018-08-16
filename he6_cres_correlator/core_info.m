% he6_cres_correlator/XSG_core_config
he6_cres_correlator_XSG_core_config_type         = 'xps_xsg';
he6_cres_correlator_XSG_core_config_param        = '';

% he6_cres_correlator/adc0
he6_cres_correlator_adc0_type         = 'xps_adc5g';
he6_cres_correlator_adc0_param        = '';
he6_cres_correlator_adc0_ip_name      = 'adc5g_dmux1_interface';

% he6_cres_correlator/adc1
he6_cres_correlator_adc1_type         = 'xps_adc5g';
he6_cres_correlator_adc1_param        = '';
he6_cres_correlator_adc1_ip_name      = 'adc5g_dmux1_interface';

% he6_cres_correlator/fft_ctrl
he6_cres_correlator_fft_ctrl_type         = 'xps_sw_reg';
he6_cres_correlator_fft_ctrl_param        = 'in';
he6_cres_correlator_fft_ctrl_ip_name      = 'opb_register_ppc2simulink';
he6_cres_correlator_fft_ctrl_addr_start   = hex2dec('01000000');
he6_cres_correlator_fft_ctrl_addr_end     = hex2dec('010000FF');

% he6_cres_correlator/gain_ctrl
he6_cres_correlator_gain_ctrl_type         = 'xps_sw_reg';
he6_cres_correlator_gain_ctrl_param        = 'in';
he6_cres_correlator_gain_ctrl_ip_name      = 'opb_register_ppc2simulink';
he6_cres_correlator_gain_ctrl_addr_start   = hex2dec('01000100');
he6_cres_correlator_gain_ctrl_addr_end     = hex2dec('010001FF');

% he6_cres_correlator/master_ctrl
he6_cres_correlator_master_ctrl_type         = 'xps_sw_reg';
he6_cres_correlator_master_ctrl_param        = 'in';
he6_cres_correlator_master_ctrl_ip_name      = 'opb_register_ppc2simulink';
he6_cres_correlator_master_ctrl_addr_start   = hex2dec('01000200');
he6_cres_correlator_master_ctrl_addr_end     = hex2dec('010002FF');

% he6_cres_correlator/master_status
he6_cres_correlator_master_status_type         = 'xps_sw_reg';
he6_cres_correlator_master_status_param        = 'out';
he6_cres_correlator_master_status_ip_name      = 'opb_register_simulink2ppc';
he6_cres_correlator_master_status_addr_start   = hex2dec('01000300');
he6_cres_correlator_master_status_addr_end     = hex2dec('010003FF');

% he6_cres_correlator/snap_0/snapshot/bram
he6_cres_correlator_snap_0_snapshot_bram_type         = 'xps_bram';
he6_cres_correlator_snap_0_snapshot_bram_param        = '65536';
he6_cres_correlator_snap_0_snapshot_bram_ip_name      = 'bram_if';
he6_cres_correlator_snap_0_snapshot_bram_addr_start   = hex2dec('01040000');
he6_cres_correlator_snap_0_snapshot_bram_addr_end     = hex2dec('0107FFFF');

% he6_cres_correlator/snap_0/snapshot/ctrl
he6_cres_correlator_snap_0_snapshot_ctrl_type         = 'xps_sw_reg';
he6_cres_correlator_snap_0_snapshot_ctrl_param        = 'in';
he6_cres_correlator_snap_0_snapshot_ctrl_ip_name      = 'opb_register_ppc2simulink';
he6_cres_correlator_snap_0_snapshot_ctrl_addr_start   = hex2dec('01080000');
he6_cres_correlator_snap_0_snapshot_ctrl_addr_end     = hex2dec('010800FF');

% he6_cres_correlator/snap_0/snapshot/status
he6_cres_correlator_snap_0_snapshot_status_type         = 'xps_sw_reg';
he6_cres_correlator_snap_0_snapshot_status_param        = 'out';
he6_cres_correlator_snap_0_snapshot_status_ip_name      = 'opb_register_simulink2ppc';
he6_cres_correlator_snap_0_snapshot_status_addr_start   = hex2dec('01080100');
he6_cres_correlator_snap_0_snapshot_status_addr_end     = hex2dec('010801FF');

% he6_cres_correlator/snap_1/snapshot/bram
he6_cres_correlator_snap_1_snapshot_bram_type         = 'xps_bram';
he6_cres_correlator_snap_1_snapshot_bram_param        = '65536';
he6_cres_correlator_snap_1_snapshot_bram_ip_name      = 'bram_if';
he6_cres_correlator_snap_1_snapshot_bram_addr_start   = hex2dec('010C0000');
he6_cres_correlator_snap_1_snapshot_bram_addr_end     = hex2dec('010FFFFF');

% he6_cres_correlator/snap_1/snapshot/ctrl
he6_cres_correlator_snap_1_snapshot_ctrl_type         = 'xps_sw_reg';
he6_cres_correlator_snap_1_snapshot_ctrl_param        = 'in';
he6_cres_correlator_snap_1_snapshot_ctrl_ip_name      = 'opb_register_ppc2simulink';
he6_cres_correlator_snap_1_snapshot_ctrl_addr_start   = hex2dec('01100000');
he6_cres_correlator_snap_1_snapshot_ctrl_addr_end     = hex2dec('011000FF');

% he6_cres_correlator/snap_1/snapshot/status
he6_cres_correlator_snap_1_snapshot_status_type         = 'xps_sw_reg';
he6_cres_correlator_snap_1_snapshot_status_param        = 'out';
he6_cres_correlator_snap_1_snapshot_status_ip_name      = 'opb_register_simulink2ppc';
he6_cres_correlator_snap_1_snapshot_status_addr_start   = hex2dec('01100100');
he6_cres_correlator_snap_1_snapshot_status_addr_end     = hex2dec('011001FF');

% he6_cres_correlator/tengbe_a/core
he6_cres_correlator_tengbe_a_core_type         = 'xps_tengbe_v2';
he6_cres_correlator_tengbe_a_core_param        = '';
he6_cres_correlator_tengbe_a_core_ip_name      = 'kat_ten_gb_eth';
he6_cres_correlator_tengbe_a_core_addr_start   = hex2dec('01104000');
he6_cres_correlator_tengbe_a_core_addr_end     = hex2dec('01107FFF');

% he6_cres_correlator/tengbe_a/ctrl
he6_cres_correlator_tengbe_a_ctrl_type         = 'xps_sw_reg';
he6_cres_correlator_tengbe_a_ctrl_param        = 'in';
he6_cres_correlator_tengbe_a_ctrl_ip_name      = 'opb_register_ppc2simulink';
he6_cres_correlator_tengbe_a_ctrl_addr_start   = hex2dec('01108000');
he6_cres_correlator_tengbe_a_ctrl_addr_end     = hex2dec('011080FF');

% he6_cres_correlator/tengbe_a/ip
he6_cres_correlator_tengbe_a_ip_type         = 'xps_sw_reg';
he6_cres_correlator_tengbe_a_ip_param        = 'in';
he6_cres_correlator_tengbe_a_ip_ip_name      = 'opb_register_ppc2simulink';
he6_cres_correlator_tengbe_a_ip_addr_start   = hex2dec('01108100');
he6_cres_correlator_tengbe_a_ip_addr_end     = hex2dec('011081FF');

% he6_cres_correlator/tengbe_a/port
he6_cres_correlator_tengbe_a_port_type         = 'xps_sw_reg';
he6_cres_correlator_tengbe_a_port_param        = 'in';
he6_cres_correlator_tengbe_a_port_ip_name      = 'opb_register_ppc2simulink';
he6_cres_correlator_tengbe_a_port_addr_start   = hex2dec('01108200');
he6_cres_correlator_tengbe_a_port_addr_end     = hex2dec('011082FF');

% he6_cres_correlator/tengbe_a/software_register
he6_cres_correlator_tengbe_a_software_register_type         = 'xps_sw_reg';
he6_cres_correlator_tengbe_a_software_register_param        = 'out';
he6_cres_correlator_tengbe_a_software_register_ip_name      = 'opb_register_simulink2ppc';
he6_cres_correlator_tengbe_a_software_register_addr_start   = hex2dec('01108300');
he6_cres_correlator_tengbe_a_software_register_addr_end     = hex2dec('011083FF');

% he6_cres_correlator/tengbe_b/core
he6_cres_correlator_tengbe_b_core_type         = 'xps_tengbe_v2';
he6_cres_correlator_tengbe_b_core_param        = '';
he6_cres_correlator_tengbe_b_core_ip_name      = 'kat_ten_gb_eth';
he6_cres_correlator_tengbe_b_core_addr_start   = hex2dec('0110C000');
he6_cres_correlator_tengbe_b_core_addr_end     = hex2dec('0110FFFF');

% he6_cres_correlator/tengbe_b/ctrl
he6_cres_correlator_tengbe_b_ctrl_type         = 'xps_sw_reg';
he6_cres_correlator_tengbe_b_ctrl_param        = 'in';
he6_cres_correlator_tengbe_b_ctrl_ip_name      = 'opb_register_ppc2simulink';
he6_cres_correlator_tengbe_b_ctrl_addr_start   = hex2dec('01110000');
he6_cres_correlator_tengbe_b_ctrl_addr_end     = hex2dec('011100FF');

% he6_cres_correlator/tengbe_b/ip
he6_cres_correlator_tengbe_b_ip_type         = 'xps_sw_reg';
he6_cres_correlator_tengbe_b_ip_param        = 'in';
he6_cres_correlator_tengbe_b_ip_ip_name      = 'opb_register_ppc2simulink';
he6_cres_correlator_tengbe_b_ip_addr_start   = hex2dec('01110100');
he6_cres_correlator_tengbe_b_ip_addr_end     = hex2dec('011101FF');

% he6_cres_correlator/tengbe_b/port
he6_cres_correlator_tengbe_b_port_type         = 'xps_sw_reg';
he6_cres_correlator_tengbe_b_port_param        = 'in';
he6_cres_correlator_tengbe_b_port_ip_name      = 'opb_register_ppc2simulink';
he6_cres_correlator_tengbe_b_port_addr_start   = hex2dec('01110200');
he6_cres_correlator_tengbe_b_port_addr_end     = hex2dec('011102FF');

% he6_cres_correlator/tengbe_b/software_register
he6_cres_correlator_tengbe_b_software_register_type         = 'xps_sw_reg';
he6_cres_correlator_tengbe_b_software_register_param        = 'out';
he6_cres_correlator_tengbe_b_software_register_ip_name      = 'opb_register_simulink2ppc';
he6_cres_correlator_tengbe_b_software_register_addr_start   = hex2dec('01110300');
he6_cres_correlator_tengbe_b_software_register_addr_end     = hex2dec('011103FF');

% he6_cres_correlator/unix_time0
he6_cres_correlator_unix_time0_type         = 'xps_sw_reg';
he6_cres_correlator_unix_time0_param        = 'in';
he6_cres_correlator_unix_time0_ip_name      = 'opb_register_ppc2simulink';
he6_cres_correlator_unix_time0_addr_start   = hex2dec('01110400');
he6_cres_correlator_unix_time0_addr_end     = hex2dec('011104FF');

% OPB to OPB bridge added at 0x1080000
OPB_to_OPB_bridge_added_at_0x1080000_type         = 'xps_opb2opb';
OPB_to_OPB_bridge_added_at_0x1080000_param        = '';

% OPB to OPB bridge added at 0x1100000
OPB_to_OPB_bridge_added_at_0x1100000_type         = 'xps_opb2opb';
OPB_to_OPB_bridge_added_at_0x1100000_param        = '';

