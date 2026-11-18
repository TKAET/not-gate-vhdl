library ieee;
use ieee.std_logic_1164.all;

entity tb_jk_ff is end entity;

architecture sim of tb_jk_ff is
    signal clk, j, k, q, q_bar : std_logic := '0';
begin
    dut: entity work.jk_ff port map (clk => clk, j => j, k => k, q => q, q_bar => q_bar);

    clocking: process
    begin
        while now < 120 ns loop
            wait for 5 ns; clk <= not clk;
        end loop;
        wait;
    end process;

    stimulus: process
    begin
        j <= '0'; k <= '0'; wait for 6 ns;
        assert q = '0' report "HOLD failed" severity failure;

        j <= '1'; k <= '0'; wait for 10 ns;
        assert q = '1' report "SET failed" severity failure;

        j <= '0'; k <= '0'; wait for 10 ns;
        assert q = '1' report "HOLD-one failed" severity failure;

        j <= '0'; k <= '1'; wait for 10 ns;
        assert q = '0' report "RESET failed" severity failure;

        j <= '1'; k <= '1'; wait for 10 ns;
        assert q = '1' report "TOGGLE 0-to-1 failed" severity failure;
        wait for 10 ns;
        assert q = '0' report "TOGGLE 1-to-0 failed" severity failure;

        report "tb_jk_ff PASS" severity note;
        wait;
    end process;
end architecture sim;
