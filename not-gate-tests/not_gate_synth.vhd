library ieee;
use ieee.std_logic_1164.all;
entity not_gate is
  port (
    a: in std_logic;
    y: out std_logic
  );
end not_gate;

library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

architecture rtl of not_gate is
  signal wrap_a: std_logic;
  signal wrap_y: std_logic;
  signal n1 : std_logic;
begin
  wrap_a <= a;
  y <= wrap_y;
  wrap_y <= n1;
  -- C:\Users\33255\Documents\Codex\2026-11-16\1-rs-latch-write-vhdl-code\work\github-repo\not_gate.vhd:13:8
  n1 <= not wrap_a;
end rtl;
