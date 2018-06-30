%ifndef FREDSTRINGMACRO
%define FREDSTRINGMACRO 1

;----------
;
;   NEWSTACKSTRING
;       - allocates memory for a string on the stack.  Returns an "empty" string of length 0
;----------
; No input arguments needed
;----------
; Returns: Address of the new String in RAX
;----------
%imacro NEWSTACKSTRING 0
    sub rsp, 256
    mov rax, rsp
    mov [rax], byte 0
%endmacro


%endif