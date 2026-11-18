library ieee;
use ieee.std_logic_1164.all;

entity tb_d_latch is end entity;

architecture sim of tb_d_latch is
    signal d, en, q, q_bar : std_logic := '0';
begin
    dut: entity work.d_latch port map (d => d, en => en, q => q, q_bar => q_bar);

    stimulus: process
    begin
        wait for 10 ns;
        d <= '1'; wait for 10 ns;
        assert q = '0' report "Latch changed while disabled" severity failure;

        en <= '1'; wait for 10 ns;
        assert q = '1' and q_bar = '0' report "Transparent HIGH failed" severity failure;

        d <= '0'; wait for 10 ns;
        assert q = '0' and q_bar = '1' report "Transparent LOW failed" severity failure;

        en <= '0'; d <= '1'; wait for 10 ns;
        assert q = '0' report "Hold failed" severity failure;

        en <= '1'; wait for 10 ns;
        assert q = '1' report "Re-enable failed" severity failure;

        report "tb_d_latch PASS" severity note;
        wait;
    end process;
end architecture sim;
