<script lang="ts">
  import { onMount } from "svelte";
  import { S3Client, AbortMultipartUploadCommand } from "@aws-sdk/client-s3";

  import accompaniment from "./assets/accompaniment.wav";
  import vocals from "./assets/vocals.wav";

  type Song = { tag: string | URL; buffer: AudioBuffer; gain: GainNode };

  const state = {
    context: null as AudioContext,
    songs: [] as Array<Song>,
  };

  const fetchSong = (url: string | URL) => {
    const xhr = new XMLHttpRequest();
    xhr.open("GET", url, true);
    xhr.responseType = "arraybuffer";
    xhr.onload = () => {
      state.context.decodeAudioData(xhr.response, (buffer) => {
        // create source
        const song: Song = {
          tag: url,
          buffer,
          gain: state.context.createGain(),
        };
        state.songs = [...state.songs, song];
        console.log(`Retrieved ${url} buffer`);
      });
    };
    xhr.send();
  };

  onMount(() => {
    const client = new S3Client({
      region: import.meta.env.AWS_REGION_STEM,
      accessKeyId: import.meta.env.AWS_ACCESS_STEM,
      secretAccessKey: import.meta.env.AWS_SECRET_STEM,
    });

    console.log(client);

    state.context = new AudioContext();

    // convert accompaniment to buffer
    fetchSong(accompaniment);
    fetchSong(vocals);
  });

  const play = (time) => {
    state.songs.forEach((song) => {
      const source = state.context.createBufferSource();
      source.buffer = song.buffer;
      source.connect(song.gain);
      song.gain.connect(state.context.destination);
      source.start(time);
    });
    console.log("Playing tracks");
  };

  const setSlider = (e: Event, song: Song) => {
    const target = e.target as HTMLInputElement;
    song.gain.gain.setTargetAtTime(
      parseFloat(target.value),
      state.context.currentTime,
      0.01
    );
  };
</script>

<main>
  <h1>STEM!?</h1>

  <button on:click={() => play(0)}>Play</button>

  {#each state.songs as song}
    <p>{song.tag}</p>
    <input
      type="range"
      min="0"
      max="1"
      step="0.01"
      on:input={(e) => setSlider(e, song)}
    />
  {/each}
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
