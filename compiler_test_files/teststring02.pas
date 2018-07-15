program teststring02;
var hw:String;i:Integer;
begin
  hw:='This will error after this line is printed.';
  writeln(hw);

  i:=0;
  while i < 255 do
	begin
		hw:=concat(hw,'*');
	end;
  writeln(hw);
end.
