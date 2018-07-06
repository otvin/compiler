program test24e;
var hw:String;
  hw2:String;
  hw3:String;
begin
  hw:='Hello ';
  hw2:='Freddy!!';
  hw3:=Concat('Hello', Concat(' we have ', ' Freddy'));
  writeln(hw3);
  writeln(Concat(hw,hw2),' yessir ',3,Concat(hw, Concat(' hiya ', ' bud ')));
end.