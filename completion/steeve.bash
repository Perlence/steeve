_steeve_completion() {
    COMPREPLY=( $( env COMP_WORDS="${COMP_WORDS[*]}" \
                   COMP_CWORD=$COMP_CWORD \
                   _STEEVE_COMPLETE=complete $1 ) )
    return 0
}

complete -F _steeve_completion -o default steeve;
