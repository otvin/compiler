program test21fc;
var q:integer; r:real; t:integer;

function functwo(var a:Integer; var b:Real):integer;
begin

  a := a + 1;
  b := b * 1.5;
  writeln(a);
  functwo := a

end;

function funcone(q:Integer):integer;
var one:integer; two:real;

begin {main}
  one := 4;
  two := 3.7;
  funcone := functwo(one,two);
end;

begin {main}
  q:=7;
  r:=9.8;
  t:=functwo(q,r);
  t:=funcone(1);
end.