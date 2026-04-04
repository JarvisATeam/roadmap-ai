#!/usr/bin/env bash
cd ~/roadmap-ai
source venv/bin/activate

clear
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                   ROADMAP-AI                               ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "  1. start     - Start systemet (refresh alt)"
echo "  2. next      - Hva skal jeg jobbe med?"
echo "  3. dash      - Åpne dashboards"
echo "  4. status    - System status"
echo "  5. watch     - Live overvåking"
echo "  6. demo      - Kjør guidet demo"
echo ""
echo "  7. add       - Legg til mission"
echo "  8. step      - Legg til steg"
echo "  9. done      - Marker steg ferdig"
echo ""
echo "  0. help      - Vis alle kommandoer"
echo "  q. quit      - Avslutt"
echo ""
read -p "Velg (1-9, 0, q): " choice

case $choice in
  1|start)  ./scripts/quickstart.sh ;;
  2|next)   roadmap smart-next ;;
  3|dash)   ./scripts/open_dashboards.sh ;;
  4|status) mc status ;;
  5|watch)  mc watch ;;
  6|demo)   ./scripts/demo_walkthrough.sh ;;
  7|add)
    read -p "Navn på mission: " name
    read -p "Type (feature/bugfix/research): " type
    roadmap add-mission "$name" --type "${type:-feature}"
    ;;
  8|step)
    read -p "Mission-kode (f.eks. FEA-1): " mission
    read -p "Beskrivelse: " desc
    read -p "Deadline (YYYY-MM-DD, enter for ingen): " due
    if [ -n "$due" ]; then
      roadmap add-step "$desc" --mission "$mission" --due "$due"
    else
      roadmap add-step "$desc" --mission "$mission"
    fi
    ;;
  9|done)
    read -p "Steg-kode (f.eks. FEA-1-S1): " step
    read -p "Grunn: " reason
    roadmap decide "$step" --approve --reason "$reason"
    ;;
  0|help)
    echo ""
    echo "ALLE KOMMANDOER:"
    echo ""
    echo "  roadmap --help        Roadmap CLI hjelp"
    echo "  mc help               Mission Control hjelp"
    echo "  cat QUICKSTART.md     Quickstart guide"
    echo ""
    ;;
  q|quit)  exit 0 ;;
  *)       echo "Ugyldig valg" ;;
esac
