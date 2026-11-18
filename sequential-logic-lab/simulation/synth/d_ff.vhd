library ieee;
use ieee.std_logic_1164.all;
entity d_ff is
  port (
    clk: in std_logic;
    d: in std_logic;
    q: out std_logic;
    q_bar: out std_logic
  );
end entity d_ff;

library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

architecture rtl of d_ff is
  signal wrap_clk: std_logic;
  signal wrap_d: std_logic;
  signal wrap_q: std_logic;
  signal wrap_q_bar: std_logic;
  signal q_i : std_logic;
  signal n8 : std_logic;
  signal n9 : std_logic := '0';
begin
  wrap_clk <= clk;
  wrap_d <= d;
  q <= wrap_q;
  q_bar <= wrap_q_bar;
  wrap_q <= q_i;
  wrap_q_bar <= n8;
  -- C:\Users\33255\Documents\Codex\2026-11-16\1-rs-latch-write-vhdl-code\vhdl\src\d_ff.vhd:14:12
  q_i <= n9; -- (isignal)
  -- C:\Users\33255\Documents\Codex\2026-11-16\1-rs-latch-write-vhdl-code\vhdl\src\d_ff.vhd:24:14
  n8 <= not q_i;
  -- C:\Users\33255\Documents\Codex\2026-11-16\1-rs-latch-write-vhdl-code\vhdl\src\d_ff.vhd:18:9
  process (wrap_clk)
  begin
    if rising_edge (wrap_clk) then
      n9 <= wrap_d;
    end if;
  end process;
end rtl;
