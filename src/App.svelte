<script lang="ts">
  import { onMount } from "svelte";

  import accompaniment from "./assets/accompaniment.wav";
  import vocals from "./assets/vocals.wav";

  let to;

  let loaded = "NEW";

  onMount(() => {
    loaded = "MOUNTED";
  });

  const acc = {
    aud: null,
    duration: 0,
    currentTime: 0,
    gain: null,
  };

  const voc = {
    aud: null,
    duration: 0,
    currentTime: 0,
    gain: null,
  };

  const load = () => {
    acc.aud.play();
    voc.aud.play();

    to = new globalThis.TIMINGSRC.TimingObject({ range: [0, 100] });
    globalThis.MCorp.mediaSync(acc.aud, to);
    globalThis.MCorp.mediaSync(voc.aud, to);

    const audioContext = new AudioContext();
    const accSource = audioContext.createMediaElementSource(acc.aud);
    acc.gain = audioContext.createGain();
    const vocSource = audioContext.createMediaElementSource(voc.aud);
    voc.gain = audioContext.createGain();

    const dest = audioContext.destination;

    accSource.connect(acc.gain).connect(dest);
    vocSource.connect(voc.gain).connect(dest);

    console.log("Fully Connected");

    loaded = "LOADED";
  };

  const play = () => {
    var v = to.query();
    if (v.position === 100 && v.velocity === 0) {
      to.update({ position: 0.0, velocity: 1.0 });
    } else to.update({ velocity: 1.0 });
  };

  const pause = () => {
    to.update({ velocity: 0.0 });
  };

  const restart = () => {
    to.update({ position: 0.0 });
  };
</script>

<main>
  <audio
    controls
    src={accompaniment}
    bind:this={acc.aud}
    bind:duration={acc.duration}
    bind:currentTime={acc.currentTime}
  />

  <audio
    controls
    src={vocals}
    bind:this={voc.aud}
    bind:duration={voc.duration}
    bind:currentTime={voc.currentTime}
  />

  <h1>STEM!?</h1>

  <div class="controls">
    {#if loaded === "MOUNTED"}
      <button on:click={load}>Load</button>
    {/if}
    <button on:click={play}>Play</button>
    <button on:click={pause}>Pause</button>
    <button on:click={restart}>Restart</button>
  </div>

  <div class="tracks">
    {#if loaded === "LOADED"}
      <div class="track">
        <div>Instrumental</div>
        <input
          type="range"
          min="0"
          max="1"
          step="0.2"
          bind:value={acc.gain.gain.value}
        />
        <progress value={acc.currentTime} max={acc.duration} />
      </div>
    {/if}

    {#if loaded === "LOADED"}
      <div class="track">
        <div>Vocals</div>
        <input
          type="range"
          min="0"
          max="1"
          step="0.2"
          bind:value={voc.gain.gain.value}
        />
        <progress value={voc.currentTime} max={voc.duration} />
      </div>
    {/if}
  </div>

  <div class="volume" />
</main>

<style>
  :root {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen,
      Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif;
  }

  main {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1em;
  }

  .controls {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    gap: 0.5em;
  }

  .controls button {
    font-size: 1.5em;
    padding: 0.5em 1em;
    border-radius: 0.25em;
    outline: none;
    border: none;
    color: #fafafa;
    background-color: #333;
  }

  .tracks {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    align-items: center;
    gap: 0.5em;
  }

  .track {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0em;
    font-size: 2em;
  }

  .track input {
    width: min(100%, 256px);
  }

  .track progress {
    max-height: 24px;
    background-color: #333;
    border-radius: 0.25em;
  }
</style>
