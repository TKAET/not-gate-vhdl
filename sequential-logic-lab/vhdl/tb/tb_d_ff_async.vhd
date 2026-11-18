library ieee;
use ieee.std_logic_1164.all;

entity tb_d_ff_async is end entity;

architecture sim of tb_d_ff_async is
    signal clk, d, set, clr, q, q_bar : std_logic := '0';
begin
    dut: entity work.d_ff_async
        port map (clk => clk, d => d, set => set, clr => clr, q => q, q_bar => q_bar);

    clocking: process
    begin
        while now < 140 ns loop
            wait for 5 ns; clk <= not clk;
        end loop;
        wait;
    end process;

    stimulus: process
    begin
        d <= '1'; wait for 6 ns;
        assert q = '1' report "Normal D capture failed" severity failure;

        clr <= '1'; wait for 2 ns;
        assert q = '0' report "Asynchronous clear failed" severity failure;
        d <= '0'; wait for 5 ns;
        assert q = '0' report "Clear was not dominant" severity failure;

        clr <= '0'; set <= '1'; wait for 2 ns;
        assert q = '1' report "Asynchronous set failed" severity failure;

        clr <= '1'; wait for 2 ns;
        assert q = '0' report "Clear priority over set failed" severity failure;

        set <= '0'; clr <= '0'; d <= '0'; wait for 11 ns;
        assert q = '0' report "Normal operation after async controls failed" severity failure;
        d <= '1'; wait for 10 ns;
        assert q = '1' report "Final normal D capture failed" severity failure;

        report "tb_d_ff_async PASS" severity note;
        wait;
    end process;
end architecture sim;
