library ieee;
use ieee.std_logic_1164.all;

-- Active-high RS latch with the same behavior as a cross-coupled NOR pair.
entity rs_latch is
    port (
        s     : in  std_logic;
        r     : in  std_logic;
        q     : out std_logic;
        q_bar : out std_logic
    );
end entity rs_latch;

architecture rtl of rs_latch is
    signal q_i     : std_logic := '0';
    signal q_bar_i : std_logic := '1';
begin
    process (s, r)
    begin
        if s = '1' and r = '0' then
            q_i     <= '1';
            q_bar_i <= '0';
        elsif s = '0' and r = '1' then
            q_i     <= '0';
            q_bar_i <= '1';
        elsif s = '1' and r = '1' then
            -- A NOR latch forces both outputs low in the forbidden condition.
            q_i     <= '0';
            q_bar_i <= '0';
        end if; -- S=R=0: hold the previous state.
    end process;

    q     <= q_i;
    q_bar <= q_bar_i;
end architecture rtl;
