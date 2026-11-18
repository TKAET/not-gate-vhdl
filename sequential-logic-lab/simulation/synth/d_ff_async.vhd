library ieee;
use ieee.std_logic_1164.all;
entity d_ff_async is
  port (
    clk: in std_logic;
    d: in std_logic;
    set: in std_logic;
    clr: in std_logic;
    q: out std_logic;
    q_bar: out std_logic
  );
end entity d_ff_async;

library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

architecture rtl of d_ff_async is
  signal wrap_clk: std_logic;
  signal wrap_d: std_logic;
  signal wrap_set: std_logic;
  signal wrap_clr: std_logic;
  signal wrap_q: std_logic;
  signal wrap_q_bar: std_logic;
  signal q_i : std_logic;
  signal n8 : std_logic;
  signal n12 : std_logic;
  signal n13 : std_logic;
  signal n14 : std_logic := '0';
begin
  wrap_clk <= clk;
  wrap_d <= d;
  wrap_set <= set;
  wrap_clr <= clr;
  q <= wrap_q;
  q_bar <= wrap_q_bar;
  wrap_q <= q_i;
  wrap_q_bar <= n12;
  -- C:\Users\33255\Documents\Codex\2026-11-16\1-rs-latch-write-vhdl-code\vhdl\src\d_ff_async.vhd:16:12
  q_i <= n14; -- (isignal)
  -- C:\Users\33255\Documents\Codex\2026-11-16\1-rs-latch-write-vhdl-code\vhdl\src\d_ff_async.vhd:22:9
  n8 <= '1' when wrap_clr = '0' else '0';
  -- C:\Users\33255\Documents\Codex\2026-11-16\1-rs-latch-write-vhdl-code\vhdl\src\d_ff_async.vhd:30:14
  n12 <= not q_i;
  -- C:\Users\33255\Documents\Codex\2026-11-16\1-rs-latch-write-vhdl-code\vhdl\src\d_ff_async.vhd:4:8
  n13 <= wrap_clr or wrap_set;
  -- C:\Users\33255\Documents\Codex\2026-11-16\1-rs-latch-write-vhdl-code\vhdl\src\d_ff_async.vhd:24:9
  process (wrap_clk, n13, n8)
  begin
    if n13 = '1' then
      n14 <= n8;
    elsif rising_edge (wrap_clk) then
      n14 <= wrap_d;
    end if;
  end process;
end rtl;
