library ieee;
use ieee.std_logic_1164.all;
use std.env.all;

entity tb_not_gate is end entity;
architecture sim of tb_not_gate is
    signal a : std_logic := '0';
    signal y : std_logic;
begin
    dut: entity work.not_gate port map(a=>a,y=>y);
    stimulus: process
    begin
        a<='0'; wait for 10 ns;
        assert y='1' report "a=0 must produce y=1" severity failure;
        report "PASS: a=0 y=1" severity note;
        a<='1'; wait for 10 ns;
        assert y='0' report "a=1 must produce y=0" severity failure;
        report "PASS: a=1 y=0" severity note;
        a<='0'; wait for 10 ns;
        assert y='1' report "Second low input failed" severity failure;
        a<='1'; wait for 10 ns;
        assert y='0' report "Second high input failed" severity failure;
        report "tb_not_gate PASS: 4 binary test vectors" severity note;
        finish;
    end process;
end architecture;
