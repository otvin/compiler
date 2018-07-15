program testproc04;
{pass in string literals into string typed parameters}
var
  s:String;
procedure concatwrapper(var a:String; b:String);
begin
  a:=concat(a,b);
end;

procedure writelnwrapper(s:String);
begin
  writeln('In the wrapper: ', s);
end;

begin {main}
  s:='Fred ';
  concatwrapper(s,'rocks!');
  writeln(s);
  writelnwrapper(s);
end.