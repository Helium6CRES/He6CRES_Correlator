library IEEE;
use IEEE.std_logic_1164.all;

entity he6_fft is
  port (
    ce_1: in std_logic; 
    clk_1: in std_logic; 
    din0_c: in std_logic_vector(49 downto 0); 
    shift: in std_logic_vector(12 downto 0); 
    sync_in: in std_logic; 
    dout0_c: out std_logic_vector(49 downto 0); 
    fft_of: out std_logic; 
    sync_out: out std_logic
  );
end he6_fft;

architecture structural of he6_fft is
begin
end structural;

