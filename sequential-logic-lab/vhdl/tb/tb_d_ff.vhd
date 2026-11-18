library ieee;
use ieee.std_logic_1164.all;

entity tb_d_ff is end entity;

architecture sim of tb_d_ff is
    signal clk, d, q, q_bar : std_logic := '0';
begin
    dut: entity work.d_ff port map (clk => clk, d => d, q => q, q_bar => q_bar);

    clocking: process
    begin
        while now < 100 ns loop
            wait for 5 ns; clk <= not clk;
        end loop;
        wait;
    end process;

    stimulus: process
    begin
        d <= '1'; wait for 6 ns;
        assert q = '1' report "First rising edge failed" severity failure;

        d <= '0'; wait for 4 ns;
        assert q = '1' report "Changed between rising edges" severity failure;
        wait for 6 ns;
        assert q = '0' report "Second rising edge failed" severity failure;

        d <= '1'; wait for 10 ns;
        assert q = '1' report "Third rising edge failed" severity failure;
        d <= '0'; wait for 4 ns;
        assert q = '1' report "Changed on falling edge" severity failure;

        report "tb_d_ff PASS" severity note;
        wait;
    end process;
end architecture sim;
