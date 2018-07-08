program testconcat05;
var i1:string;z:integer;
begin
  z:=0;
  i1 := '';
  while z < 7 do begin
    i1 := concat (i1, '*');
    z := z + 1;
  end;
  writeln(i1);

end.