library ieee;
use ieee.std_logic_1164.all;
entity d_latch is
  port (
    d: in std_logic;
    en: in std_logic;
    q: out std_logic;
    q_bar: out std_logic
  );
end entity d_latch;

library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

architecture rtl of d_latch is
  signal wrap_d: std_logic;
  signal wrap_en: std_logic;
  signal wrap_q: std_logic;
  signal wrap_q_bar: std_logic;
  signal q_i : std_logic;
  signal n7 : std_logic;
  signal n8 : std_logic;
begin
  wrap_d <= d;
  wrap_en <= en;
  q <= wrap_q;
  q_bar <= wrap_q_bar;
  wrap_q <= q_i;
  wrap_q_bar <= n7;
  -- C:\Users\33255\Documents\Codex\2026-11-16\1-rs-latch-write-vhdl-code\vhdl\src\d_latch.vhd:14:12
  q_i <= n8; -- (isignal)
  -- C:\Users\33255\Documents\Codex\2026-11-16\1-rs-latch-write-vhdl-code\vhdl\src\d_latch.vhd:24:14
  n7 <= not q_i;
  -- C:\Users\33255\Documents\Codex\2026-11-16\1-rs-latch-write-vhdl-code\vhdl\src\d_latch.vhd:14:12
  n8 <= wrap_d when wrap_en = '1' else n8;
end rtl;
