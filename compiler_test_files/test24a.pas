program test24a;
var hw:String;
begin
  hw:='This will error after this line is printed.';
  writeln(hw);

  hw:='This will error after this line is printed. 0123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789';
  writeln(hw);
end.