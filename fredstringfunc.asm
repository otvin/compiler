;----------
;
;   fredstringfunc.asm
;   copyright 2018 M. "Fred" Fredericks
;   All Rights Reserved
;   string functions for the Fred compiler
;
;----------

extern prtstrz  ; from nsm64
extern prtstr   ; from nsm64
extern newline  ; from nsm64
extern exit     ; from nsm64

extern malloc  ; from libc
extern free    ; from libc


global newstring
global freestring
global printstring
global literaltostring
global stringlength

section .data

fred_err_malloc_failed db "Memory allocation failed",0
fred_err_str_too_large db "Maximum string length exceeded",0 
fred_err_invalid_size  db "Invalid string size",0




;----------
;   A Pascal String is a data type that can hold up to 255 characters.  The first byte is an unsigned int 
;   containing the length.  The remaining 255 bytes are the string data itself.  Unlike strings in C, 
;   Pascal Strings are not null-terminated.  
;----------   


;----------
;
;   newstring
;       - allocates memory for a string, returns an "empty" string of length 0
;----------
; No input arguments needed
;----------
; Returns: Address of the new String in RAX
;----------
newstring:
    mov rdi, 256
    call malloc
    ; if malloc fails, rax will be 0
    test rax, rax
    je .err1
    ; length of the string goes in first byte, so we zero that out.
    mov [rax], byte 0  
    ret
.err1:
    mov rdi, fred_err_malloc_failed
    call prtstrz
    call newline
    call exit    

;----------
;
;   freestring
;       - deallocates memory for a string
;
;----------
; RDI: Pointer to the address of the String
;----------
; Returns: None
;----------
freestring:
    call free  ; RDI already points to the string to be freed
    ret


;----------
;
;   printstring
;       - displays the contents of the string to stdout
;----------
; RDI: Pointer to the address of the String
;----------
; Returns: None
;----------
printstring:
    ; rsi takes the length of the string as a parameter.  "sil" is lowest byte of rsi.
    mov sil, byte [rdi]
    ; rdi takes the pointer to the start of the string, which is one byte after rdi.
    inc rdi ; functions are allowed to trash RDI
    call prtstr
    ret

;----------
;
;   stringlength
;       - displays the length of a String (which is the first byte)
;----------
; RDI: Pointer to the address of the String
;----------
; Returns: RAX (AL actually) will contain the length
;----------
stringlength:
    xor rax,rax
    mov al,byte[RDI]
    ret


;----------
;
;   literaltostring
;       - creates a String, with dynamic memory allocated, containing the literal.  String literals are zero-terminated.
;----------
; RDI: Pointer to the address of the string literal
;----------
; Returns: Address of the new String in RAX
;----------

literaltostring:
    ; need to preserve RDI in case newstring or something it calls (like malloc) trashes it
    push RDI
    call newstring  
    ; RAX now has the pointer to the String that we will want to return
    
    pop RDI
    ; RCX - used to walk the literal 
    ; RDX - used to walk the new String
    ; R8 - used to assign the character to the String
    ; R9 - used to count characters
    mov rcx, rdi
    mov rdx, rax
    inc rdx
    mov r9, 0
.loop:
    ; if we see the null terminator we are done
    cmp byte [rcx], 0
    je .done
    ; validate we can increase the length of the String
    cmp r9, 255
    jge .err1
    mov r8b, byte[rcx]
    mov byte [rdx], r8b
    inc r9
    inc rdx
    inc rcx
    jmp .loop
.done:
    mov byte [rax], r9b ; put the size of the string as the first byte of RAX.                                
    ret
.err1:                
    mov rdi, fred_err_str_too_large
    call prtstrz
    call newline
    call exit      

