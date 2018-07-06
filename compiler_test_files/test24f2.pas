program test24f2;
var hw:String;
  hw2:String;
procedure x(a:integer);
var z:integer;
begin
  if a > 0 then
    begin
      z:= 1;
      while z <= a do
        begin
          writeln(concat('Doing the loop','*'));
          z := z + 1;
        end;
    end
  else
    writeln('nope!')
end;
begin
  hw:='Main ';
  hw2:='Concats';
  writeln(Concat(hw,hw2),' yessir ');
  x(-2);
  x(3);
  x(4);
  x(2);
end.