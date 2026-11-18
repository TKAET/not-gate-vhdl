library ieee;
use ieee.std_logic_1164.all;

entity jk_ff is
    port (
        clk   : in  std_logic;
        j     : in  std_logic;
        k     : in  std_logic;
        q     : out std_logic;
        q_bar : out std_logic
    );
end entity jk_ff;

architecture rtl of jk_ff is
    signal q_i : std_logic := '0';
begin
    process (clk)
    begin
        if rising_edge(clk) then
            case j & k is
                when "00"   => null;       -- Hold
                when "01"   => q_i <= '0'; -- Reset
                when "10"   => q_i <= '1'; -- Set
                when "11"   => q_i <= not q_i; -- Toggle
                when others => q_i <= 'X';
            end case;
        end if;
    end process;

    q     <= q_i;
    q_bar <= not q_i;
end architecture rtl;
