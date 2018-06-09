program test12b;

function addV2(c:Integer; d:Integer):integer;
begin

    addV2 := c+d;
    { previously,invoking any function call after assigning to the result would lead to result geting corrupted}
    writeln(0)
end;

begin

    writeln(addV2(6,9))

end.
