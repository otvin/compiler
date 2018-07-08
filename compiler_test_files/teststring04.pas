program teststring04;
{test Strings as local variables in a procedure}
var hw:String;
  hw2:String;
procedure x(a:integer);
var i1:string; z:integer;
begin
  if a > 0 then
    begin
      z:= 1;
      i1 := 'doing the loop ';
      while z <= a do
        begin
          i1 := concat(i1, '*');
          z := z + 1;
        end;
        writeln(i1);
    end
  else
    writeln('nope!')
end;
begin
  hw:='Main ';
  hw2:='Concats';
  writeln(Concat(hw,hw2),' yessir ');
  x(-2);
  x(17);
  x(47);
  x(9);
end.


