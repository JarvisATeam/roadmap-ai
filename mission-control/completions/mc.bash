_mc_completions() {
  local cur prev
  COMPREPLY=()
  cur="${COMP_WORDS[COMP_CWORD]}"
  prev="${COMP_WORDS[COMP_CWORD-1]}"

  local commands="run status doctor init bootstrap prompt selftest help"
  local prompt_modes="list auto build plan architect dream memory security guard security2"
  local bootstrap_flags="--dry-run --skip-hooks --skip-launchagent --help"

  if [[ ${COMP_CWORD} -eq 1 ]]; then
    COMPREPLY=( $(compgen -W "${commands}" -- "${cur}") )
    return 0
  fi

  case "${COMP_WORDS[1]}" in
    prompt)
      COMPREPLY=( $(compgen -W "${prompt_modes}" -- "${cur}") )
      return 0
      ;;
    init|bootstrap)
      COMPREPLY=( $(compgen -W "${bootstrap_flags}" -- "${cur}") )
      return 0
      ;;
  esac
}

complete -F _mc_completions ./bin/mc.sh
complete -F _mc_completions mc.sh
