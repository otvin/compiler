%ifndef FREDSTRINGMACRO
%define FREDSTRINGMACRO 1

%define FREDSTRINGSIZE 255

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
    sub rsp, FREDSTRINGSIZE + 1
    mov rax, rsp
    mov [rax], byte 0
%endmacro

%idefine FREESTACKSTRING add rsp, FREDSTRINGSIZE + 1

%endif