var map = L.map('map', {
  crs: L.CRS.Simple,
  minZoom: 2,
  maxZoom: 8, // set max zoom level
  maxBounds: [[-50, -50], [150, 150]] // set panning bounds
}).setView([40, 50], 3);

function base64ToArrayBuffer(base64) {
  var binaryString = atob(base64);
  var bytes = new Uint8Array(binaryString.length);
  for (var i = 0; i < binaryString.length; i++) {
      bytes[i] = binaryString.charCodeAt(i);
  }
  return bytes.buffer;
}

function decodePoints(encoded) {
  var bytes = base64ToArrayBuffer(encoded);
  var data = new Float32Array(bytes);
  var points = [];
  for (var i = 0; i < data.length; i += 2) {
    points.push([data[i], data[i + 1]]);
  }
  return points;
}

function setPopup(gif) {
  $('.popup').removeClass('hidden');
  if (gif.endsWith('.gif')) {
    $('.popup-content').html(`<img width="100%" src="${gif}"/>`);
  } else if (gif.endsWith('.mp4')) {
    $('.popup-content').html(`<video width="100%" autoplay loop muted><source src="${gif}" type="video/mp4"></video>`);
  } else {
    console.error("Invalid gif file");
  }
}

$('.popup').click(function() {
  $('.popup').addClass('hidden');
});

function loadPuzzle(puzzle_id) {
  window.PUZZLE = puzzle_id;
  fetch(`./data/solutions/${puzzle_id}.json`).then(r => r.json()).then(data => {
    $('h1').text(data.name);
  
    for(var i = 0; i < data.solutions.length; i++) {
      const solution = data.solutions[i];
      try {
        solution.points = decodePoints(solution.shape);
        const polygon = L.polygon(solution.points, {
          color: d3.schemeSet1[solution.color+1],
          weight: 1,
          opacity: 1,
          fillOpacity: 0.6,
        }).addTo(map);
        polygon.on('mouseover', function() {
          this.setStyle({
            fillOpacity: 0.9,
          });
        });
        polygon.on('mouseout', function() {
          this.setStyle({
            fillOpacity: 0.6,
          });
        });
        polygon.on('click', function() {
          setPopup(solution.gif);
        });
        polygon.bindTooltip(`${solution.metrics.cycles}c / ${solution.metrics.area}a / ${solution.metrics.cost}g`,{
          direction: 'center',
        })
        // polygon.bindTooltip(`${solution.id}`,{direction: 'center',})
      } catch(e) {
        console.error(e, solution);
        continue;
      }
    }
  });
}

fetch('./data/puzzles.json').then(r => r.json()).then(data => {
  window.autoCompleteJS = new autoComplete({
    placeHolder: "Search for Puzzle...",
    data: {
      src: data,
      keys: ['name'],
      cache: true,
    },
    resultItem: {
      highlight: true,
    },
    selector:'#search',
    submit: true,
    events: {
      input: {
        selection(e) {
          const selection = e.detail.selection.value;
          window.location.search = `?${selection.id}`;
        }
      }
    }
  });
  if (window.PUZZLE == undefined) {
    // load a random puzzle
    const random_puzzle = data[Math.floor(Math.random() * data.length)];
    loadPuzzle(random_puzzle.id);
  }
})

fetch('./data/last_updated').then(r => r.text()).then(data => {
  const last_updated = (new Date(data)).toLocaleString([], {
    dateStyle: 'medium',
    timeStyle: 'short',
  });
  $('.leaflet-control-attribution').html(`<a href="https://github.com/benjameep/opus-magnum-ternary-plots">last updated on ${last_updated}</a>`);
});

const puzzle_id = window.location.search.slice(1)
if (puzzle_id) {
  loadPuzzle(puzzle_id);
}