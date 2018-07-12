program testproc02;
{Test passing strings byval into procedures}
var q:string;r:string;

procedure concatwrapper(a:string;b:string);
begin
  writeln(a);
  writeln(b);
  writeln(concat(a,b));
  a:='Oops';
end;

procedure concatwrapper2(a:string;b:string);
var c:string;
begin
  writeln(a);
  writeln(b);
  c:=concat(a,b);
  writeln(c);
  a:='Oops';
end;

begin {main}
  q:='hello ';
  r:='world';
  concatwrapper(q,r);
  r:='Fred';
  concatwrapper2(q,r);
end.
