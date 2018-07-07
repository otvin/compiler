program testreal08;{comment}

{test bugfix of a comment right after the program statement, also tests passing int values 
 for real parameters}

var myint:integer;
function abs(i:real):real;
begin
  if i < 0.0 then
    abs := -1.0 * i
  else
    abs := i
end;

begin {main}
  myint := -4;
  writeln(abs(1));
  writeln(abs(myint));
end.
