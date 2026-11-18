library ieee;
use ieee.std_logic_1164.all;

entity tb_rs_latch is end entity;

architecture sim of tb_rs_latch is
    signal s, r, q, q_bar : std_logic := '0';
begin
    dut: entity work.rs_latch port map (s => s, r => r, q => q, q_bar => q_bar);

    stimulus: process
    begin
        wait for 10 ns;
        s <= '1'; wait for 10 ns;
        assert q = '1' and q_bar = '0' report "SET failed" severity failure;

        s <= '0'; wait for 10 ns;
        assert q = '1' and q_bar = '0' report "HOLD-after-SET failed" severity failure;

        r <= '1'; wait for 10 ns;
        assert q = '0' and q_bar = '1' report "RESET failed" severity failure;

        r <= '0'; wait for 10 ns;
        assert q = '0' and q_bar = '1' report "HOLD-after-RESET failed" severity failure;

        s <= '1'; r <= '1'; wait for 10 ns;
        assert q = '0' and q_bar = '0' report "FORBIDDEN condition failed" severity failure;

        report "tb_rs_latch PASS" severity note;
        wait;
    end process;
end architecture sim;
