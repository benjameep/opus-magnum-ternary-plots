var map = L.map('map', {
  crs: L.CRS.Simple,
  minZoom: 2,
  maxZoom: 8, // set max zoom level
  maxBounds: [[-50, -50], [150, 150]] // set panning bounds
}).setView([40, 50], 3);

COLORS = "a6cee31f78b4b2df8a33a02cfb9a99e31a1cfdbf6fff7f00cab2d66a3d9affff99b15928"
function getColor(idx, highlighted=false) {
  console.assert(idx >= 0 && idx < 6, "idx out of range");
  console.assert(typeof highlighted === "boolean", "highlighted must be a boolean");
  idx = (idx * 2 + highlighted) * 6
  return '#' + COLORS.slice(idx, idx+6);
}

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

window.PUZZLE = window.location.search.split('?')[1];
if (!window.PUZZLE) {
  window.PUZZLE = 'P060';
}
fetch(`/data/solutions/${window.PUZZLE}.json`).then(r => r.json()).then(data => {
  $('h1').text(data.name);
  console.log('last updated on', new Date(data.last_updated))

  for(var i = 0; i < data.solutions.length; i++) {
    const solution = data.solutions[i];
    try {
      solution.points = decodePoints(solution.shape);
      solution.$ = L.polygon(solution.points, {
        color: getColor(solution.color, true),
        weight: 1,
        opacity: 1,
        fillOpacity: 0.6,
      }).addTo(map);
      solution.$.on('mouseover', function() {
        this.setStyle({
          fillOpacity: 0.9,
        });
      });
      solution.$.on('mouseout', function() {
        this.setStyle({
          fillOpacity: 0.6,
        });
      });
      solution.$.on('click', function() {
        setPopup(solution.gif);
      });
    } catch(e) {
      console.error(e, solution);
      continue;
    }
  }
})

fetch('/data/puzzles.json').then(r => r.json()).then(data => {
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
          window.location = `/?${selection.id}`;
        }
      }
    }
  });
})