library ieee;
use ieee.std_logic_1164.all;
entity rs_latch is
  port (
    s: in std_logic;
    r: in std_logic;
    q: out std_logic;
    q_bar: out std_logic
  );
end entity rs_latch;

library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

architecture rtl of rs_latch is
  signal wrap_s: std_logic;
  signal wrap_r: std_logic;
  signal wrap_q: std_logic;
  signal wrap_q_bar: std_logic;
  signal q_i : std_logic;
  signal q_bar_i : std_logic;
  signal n6 : std_logic;
  signal n7 : std_logic;
  signal n8 : std_logic;
  signal n9 : std_logic;
  signal n10 : std_logic;
  signal n16 : std_logic;
  signal n18 : std_logic;
  signal n20 : std_logic;
  signal n22 : std_logic;
  signal n24 : std_logic;
  signal n25 : std_logic;
  signal n26 : std_logic;
  signal n27 : std_logic;
  signal n28 : std_logic;
  signal n29 : std_logic;
begin
  wrap_s <= s;
  wrap_r <= r;
  q <= wrap_q;
  q_bar <= wrap_q_bar;
  wrap_q <= q_i;
  wrap_q_bar <= q_bar_i;
  -- C:\Users\33255\Documents\Codex\2026-11-16\1-rs-latch-write-vhdl-code\vhdl\src\rs_latch.vhd:15:12
  q_i <= n26; -- (isignal)
  -- C:\Users\33255\Documents\Codex\2026-11-16\1-rs-latch-write-vhdl-code\vhdl\src\rs_latch.vhd:16:12
  q_bar_i <= n29; -- (isignal)
  -- C:\Users\33255\Documents\Codex\2026-11-16\1-rs-latch-write-vhdl-code\vhdl\src\rs_latch.vhd:20:26
  n6 <= not wrap_r;
  -- C:\Users\33255\Documents\Codex\2026-11-16\1-rs-latch-write-vhdl-code\vhdl\src\rs_latch.vhd:20:20
  n7 <= n6 and wrap_s;
  -- C:\Users\33255\Documents\Codex\2026-11-16\1-rs-latch-write-vhdl-code\vhdl\src\rs_latch.vhd:23:17
  n8 <= not wrap_s;
  -- C:\Users\33255\Documents\Codex\2026-11-16\1-rs-latch-write-vhdl-code\vhdl\src\rs_latch.vhd:23:23
  n9 <= wrap_r and n8;
  -- C:\Users\33255\Documents\Codex\2026-11-16\1-rs-latch-write-vhdl-code\vhdl\src\rs_latch.vhd:26:23
  n10 <= wrap_r and wrap_s;
  -- C:\Users\33255\Documents\Codex\2026-11-16\1-rs-latch-write-vhdl-code\vhdl\src\rs_latch.vhd:23:9
  n16 <= '0' when n9 = '0' else '0';
  -- C:\Users\33255\Documents\Codex\2026-11-16\1-rs-latch-write-vhdl-code\vhdl\src\rs_latch.vhd:23:9
  n18 <= '0' when n9 = '0' else '1';
  -- C:\Users\33255\Documents\Codex\2026-11-16\1-rs-latch-write-vhdl-code\vhdl\src\rs_latch.vhd:20:9
  n20 <= n16 when n7 = '0' else '1';
  -- C:\Users\33255\Documents\Codex\2026-11-16\1-rs-latch-write-vhdl-code\vhdl\src\rs_latch.vhd:20:9
  n22 <= n18 when n7 = '0' else '0';
  -- C:\Users\33255\Documents\Codex\2026-11-16\1-rs-latch-write-vhdl-code\vhdl\src\rs_latch.vhd:15:12
  n24 <= n10 or n9;
  -- C:\Users\33255\Documents\Codex\2026-11-16\1-rs-latch-write-vhdl-code\vhdl\src\rs_latch.vhd:15:12
  n25 <= n24 or n7;
  -- C:\Users\33255\Documents\Codex\2026-11-16\1-rs-latch-write-vhdl-code\vhdl\src\rs_latch.vhd:15:12
  n26 <= n20 when n25 = '1' else n26;
  -- C:\Users\33255\Documents\Codex\2026-11-16\1-rs-latch-write-vhdl-code\vhdl\src\rs_latch.vhd:16:12
  n27 <= n10 or n9;
  -- C:\Users\33255\Documents\Codex\2026-11-16\1-rs-latch-write-vhdl-code\vhdl\src\rs_latch.vhd:16:12
  n28 <= n27 or n7;
  -- C:\Users\33255\Documents\Codex\2026-11-16\1-rs-latch-write-vhdl-code\vhdl\src\rs_latch.vhd:16:12
  n29 <= n22 when n28 = '1' else n29;
end rtl;
