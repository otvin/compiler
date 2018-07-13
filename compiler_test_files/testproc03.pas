program testproc03;
{test byref String parameters to procedures}
var s:string;

procedure boo(var s:string);
begin
  s:=concat(s,'+42');
  writeln(s);
end;

procedure duh(s:string);
begin
  writeln('before: ', s);
  boo(s);
  writeln('after: ', s);
end;

procedure fakedoubler(s:string);
begin
  s:=concat(s,s);
end;

procedure realdoubler(var s:string);
begin
  s:=concat(s,s);
end;

begin
  s:='meaning of life';
  boo(s);
  writeln('now it equals ',s);
  s:='what is your name?';
  duh(s);
  writeln('and now it equals ',s);
  s:='doubletrouble';
  fakedoubler(s);
  writeln(s);
  realdoubler(s);
  writeln(s);
end.