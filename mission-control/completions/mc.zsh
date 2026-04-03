#compdef mc.sh ./bin/mc.sh

_arguments \
  '1:command:(run status doctor init bootstrap prompt selftest help)' \
  '*::arg:->args'

case $state in
  args)
    case $words[2] in
      prompt)
        _values 'prompt mode' list auto build plan architect dream memory security guard security2
        ;;
      init|bootstrap)
        _values 'bootstrap flags' --dry-run --skip-hooks --skip-launchagent --help
        ;;
    esac
    ;;
esac
