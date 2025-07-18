const { JSDOM } = require('jsdom');

function generateCSSSelectors(htmlString) {
  const dom = new JSDOM(htmlString);
  const doc = dom.window.document;
  const selectors = [];

  const inputs = doc.querySelectorAll('input');
  inputs.forEach(input => {
    let selector = 'input';
    if (input.type) selector += `[type="${input.type}"]`;
    if (input.name) selector += `[name="${input.name}"]`;
    if (input.id) selector = `#${input.id}`; // ID takes precedence
    if (input.className) {
        const classes = input.className.split(' ');
        classes.forEach(cls => selector += `.${cls}`);
    }

    selectors.push(selector);
  });

  const buttons = doc.querySelectorAll('button');
  buttons.forEach(button => {
    let selector = 'button';
    if (button.type) selector += `[type="${button.type}"]`;
    if (button.id) selector = `#${button.id}`; // ID takes precedence
    if (button.className) {
        const classes = button.className.split(' ');
        classes.forEach(cls => selector += `.${cls}`);
    }
    selectors.push(selector);
  });

  return selectors.join(', '); // Join selectors with commas
}

const htmlString = `
 '<button class="vjs-play-control vjs-control vjs-button" type="button" title="Play" aria-disabled="false">',
  '<button class="vjs-mute-control vjs-control vjs-button vjs-vol-0" type="button" title="Unmute" aria-disabled="false">',
  '<button class="vjs-seek-to-live-control vjs-control" type="button" title="Seek to live, currently behind live" aria-disabled="false">',
  '<button class="vjs-chapters-button vjs-menu-button vjs-menu-button-popup vjs-button" type="button" aria-disabled="false" title="Chapters" aria-haspopup="true" aria-expanded="false">',
  '<button class="vjs-descriptions-button vjs-menu-button vjs-menu-button-popup vjs-button" type="button" aria-disabled="false" title="Descriptions" aria-haspopup="true" aria-expanded="false">',
  '<button class="vjs-audio-button vjs-menu-button vjs-menu-button-popup vjs-button" type="button" aria-disabled="false" title="Audio Track" aria-haspopup="true" aria-expanded="false">',
  '<button type="button" class="vjs-default-button" title="restore all settings to the default values">',    
  '<button type="button" class="vjs-done-button">',
  '<button class="vjs-close-button vjs-control vjs-button" type="button" aria-disabled="false" title="Close Modal Dialog">',
  '<button type="button" aria-label="Tap Watch now to see broadcast in immersive view" title="" class="watchNow--1KAMD persistent--Pt2B3 watchNow--2Q8Jd" data-test-id="watchNow" data-csa-c-action="ingress" data-csa-c-type="action" data-csa-c-channel="That Greencorner by Khushboo" data-csa-c-title="Make Your Home Christmas Ready: With Finds Under ₹500" data-csa-c-id="iczu2j-raym0u-muydwl-sw2fu9">',
  '<button type="button" aria-label="Unmute" title="Unmute" class="muteButton--2YyOU">',
  '<button type="button" aria-label="" title="" class="playButton--wDABG playPauseButton--uRVns paused--3RITy persistent--Pt2B3">'
`;

const cssSelectors = generateCSSSelectors(htmlString);
console.log(cssSelectors);