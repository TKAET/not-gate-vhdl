library ieee;
use ieee.std_logic_1164.all;
use std.textio.all;
use std.env.all;

-- Run exactly the same ordered CSV vectors as the Logisim propagation engine.
entity tb_gate_vectors is
    generic (design_name : string := "rs_latch"; vector_file : string := "rs_latch.csv");
end entity;

architecture sim of tb_gate_vectors is
    signal s, r, d, en, clk, j, k, aset, clr : std_logic := '0';
    signal qr, qrb, ql, qlb, qd, qdb, qj, qjb, qa, qab : std_logic;
    signal q, qb : std_logic;
    function bit_value(c : character) return std_logic is
    begin
        if c='1' then return '1'; else return '0'; end if;
    end function;
begin
    rs: entity work.rs_latch port map(s,r,qr,qrb);
    dl: entity work.d_latch port map(d,en,ql,qlb);
    df: entity work.d_ff port map(clk,d,qd,qdb);
    jk: entity work.jk_ff port map(clk,j,k,qj,qjb);
    af: entity work.d_ff_async port map(clk,d,aset,clr,qa,qab);
    q <= qr when design_name="rs_latch" else ql when design_name="d_latch" else
         qd when design_name="d_ff" else qj when design_name="jk_ff" else qa;
    qb <= qrb when design_name="rs_latch" else qlb when design_name="d_latch" else
          qdb when design_name="d_ff" else qjb when design_name="jk_ff" else qab;
    stimulus: process
        file vectors : text open read_mode is vector_file;
        variable row : line;
        variable values : string(1 to 6);
        variable ch : character;
        variable count, n : natural := 0;
    begin
        readline(vectors,row); -- header
        while not endfile(vectors) loop
            readline(vectors,row);
            n:=0;
            while row'length>0 loop
                read(row,ch);
                if ch/=',' and ch/=' ' then n:=n+1; values(n):=ch; end if;
            end loop;
            if n>0 then
                count:=count+1;
                if design_name="rs_latch" then s<=bit_value(values(1)); r<=bit_value(values(2));
                elsif design_name="d_latch" then d<=bit_value(values(1)); en<=bit_value(values(2));
                elsif design_name="d_ff" then d<=bit_value(values(1)); clk<=bit_value(values(2));
                elsif design_name="jk_ff" then j<=bit_value(values(1)); k<=bit_value(values(2)); clk<=bit_value(values(3));
                elsif design_name="d_ff_async" then d<=bit_value(values(1)); clk<=bit_value(values(2)); aset<=bit_value(values(3)); clr<=bit_value(values(4));
                else assert false report "Unknown design_name" severity failure;
                end if;
                wait for 10 ns;
                if values(n-1)/='-' then
                    assert q=bit_value(values(n-1)) report design_name & " Q mismatch at row " & integer'image(count) severity failure;
                end if;
                if values(n)/='-' then
                    assert qb=bit_value(values(n)) report design_name & " Q_bar mismatch at row " & integer'image(count) severity failure;
                end if;
            end if;
        end loop;
        report "VHDL/LOGISIM VECTOR EQUIVALENCE PASS: " & design_name & " rows=" & integer'image(count) severity note;
        finish;
    end process;
end architecture;
