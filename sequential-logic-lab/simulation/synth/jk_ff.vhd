library ieee;
use ieee.std_logic_1164.all;
entity jk_ff is
  port (
    clk: in std_logic;
    j: in std_logic;
    k: in std_logic;
    q: out std_logic;
    q_bar: out std_logic
  );
end entity jk_ff;

library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

architecture rtl of jk_ff is
  signal wrap_clk: std_logic;
  signal wrap_j: std_logic;
  signal wrap_k: std_logic;
  signal wrap_q: std_logic;
  signal wrap_q_bar: std_logic;
  signal q_i : std_logic;
  signal n6 : std_logic_vector (1 downto 0);
  signal n8 : std_logic;
  signal n10 : std_logic;
  signal n12 : std_logic;
  signal n13 : std_logic;
  signal n15 : std_logic;
  signal n16 : std_logic_vector (3 downto 0);
  signal n20 : std_logic;
  signal n23 : std_logic;
  signal n24 : std_logic := '0';
begin
  wrap_clk <= clk;
  wrap_j <= j;
  wrap_k <= k;
  q <= wrap_q;
  q_bar <= wrap_q_bar;
  wrap_q <= q_i;
  wrap_q_bar <= n23;
  -- C:\Users\33255\Documents\Codex\2026-11-16\1-rs-latch-write-vhdl-code\vhdl\src\jk_ff.vhd:15:12
  q_i <= n24; -- (isignal)
  -- C:\Users\33255\Documents\Codex\2026-11-16\1-rs-latch-write-vhdl-code\vhdl\src\jk_ff.vhd:20:20
  n6 <= wrap_j & wrap_k;
  -- C:\Users\33255\Documents\Codex\2026-11-16\1-rs-latch-write-vhdl-code\vhdl\src\jk_ff.vhd:21:17
  n8 <= '1' when n6 = "00" else '0';
  -- C:\Users\33255\Documents\Codex\2026-11-16\1-rs-latch-write-vhdl-code\vhdl\src\jk_ff.vhd:22:17
  n10 <= '1' when n6 = "01" else '0';
  -- C:\Users\33255\Documents\Codex\2026-11-16\1-rs-latch-write-vhdl-code\vhdl\src\jk_ff.vhd:23:17
  n12 <= '1' when n6 = "10" else '0';
  -- C:\Users\33255\Documents\Codex\2026-11-16\1-rs-latch-write-vhdl-code\vhdl\src\jk_ff.vhd:24:39
  n13 <= not q_i;
  -- C:\Users\33255\Documents\Codex\2026-11-16\1-rs-latch-write-vhdl-code\vhdl\src\jk_ff.vhd:24:17
  n15 <= '1' when n6 = "11" else '0';
  -- C:\Users\33255\Documents\Codex\2026-11-16\1-rs-latch-write-vhdl-code\vhdl\src\jk_ff.vhd:20:13
  n16 <= n15 & n12 & n10 & n8;
  -- C:\Users\33255\Documents\Codex\2026-11-16\1-rs-latch-write-vhdl-code\vhdl\src\jk_ff.vhd:20:13
  with n16 select n20 <=
    n13 when "1000",
    '1' when "0100",
    '0' when "0010",
    q_i when "0001",
    'X' when others;
  -- C:\Users\33255\Documents\Codex\2026-11-16\1-rs-latch-write-vhdl-code\vhdl\src\jk_ff.vhd:31:14
  n23 <= not q_i;
  -- C:\Users\33255\Documents\Codex\2026-11-16\1-rs-latch-write-vhdl-code\vhdl\src\jk_ff.vhd:19:9
  process (wrap_clk)
  begin
    if rising_edge (wrap_clk) then
      n24 <= n20;
    end if;
  end process;
end rtl;
