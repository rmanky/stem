<script lang="ts">
  import { onDestroy, onMount } from "svelte";
  import { S3Client, GetObjectCommand } from "@aws-sdk/client-s3";

  const attack = 0.01;
  const decay = 0.1;

  type Song = {
    tag: string;
    buffer: AudioBuffer;
    gain: GainNode;
    gainValue: number;
    solo: boolean;
  };

  const state = {
    keys: ["accompaniment.mp3", "vocals.mp3"],
    context: null as AudioContext,
    songs: [] as Array<Song>,
    soloSong: null as string | null,
  };

  const fetchSong = async (client: S3Client, key: string) => {
    const response = await client.send(
      new GetObjectCommand({
        Bucket: import.meta.env.VITE_AWS_BUCKET_STEM as string,
        Key: key,
      })
    );

    const stream = response.Body as ReadableStream;

    const arrayBuffer = await new Response(stream).arrayBuffer();
    state.context.decodeAudioData(arrayBuffer, (buffer) => {
      // create source
      const song: Song = {
        tag: key,
        buffer,
        gain: state.context.createGain(),
        gainValue: 1.0,
        solo: false,
      };
      state.songs = [...state.songs, song];
      console.log(`Retrieved ${key} buffer`);
    });
  };

  onMount(async () => {
    const client = new S3Client({
      region: import.meta.env.VITE_AWS_REGION_STEM as string,
      credentials: {
        accessKeyId: import.meta.env.VITE_AWS_ACCESS_STEM as string,
        secretAccessKey: import.meta.env.VITE_AWS_SECRET_STEM as string,
      },
    });

    console.log(import.meta.env.VITE_AWS_REGION_STEM);

    state.context = new AudioContext();

    // convert accompaniment to buffer
    for (const key of state.keys) {
      fetchSong(client, key);
    }
  });

  onDestroy(() => {
    console.log("Destroying context");
    state.context.close();
  });

  const play = (time) => {
    Object.values(state.songs).forEach((song) => {
      const source = state.context.createBufferSource();
      source.buffer = song.buffer;
      source.connect(song.gain);
      song.gain.connect(state.context.destination);
      source.start(state.context.currentTime + time);
    });
    console.log("Playing tracks");
  };

  const setSlider = (e: Event, song: Song) => {
    const target = e.target as HTMLInputElement;
    const val = parseFloat(target.value);
    song.gain.gain.setTargetAtTime(val, state.context.currentTime, attack);
    song.gainValue = val;
    state.songs = [...state.songs];
  };

  const setSolo = (soloSong: Song) => {
    state.songs.forEach((song) => {
      const isSong = song === soloSong;
      song.gain.gain.setTargetAtTime(
        isSong ? 1.0 : 0.0,
        state.context.currentTime,
        attack
      );
      song.solo = isSong;
    });
    state.songs = [...state.songs];
    state.soloSong = soloSong.tag;
  };

  const resetGains = () => {
    state.songs.forEach((song) => {
      song.gain.gain.setTargetAtTime(
        song.gainValue,
        state.context.currentTime,
        decay
      );
      song.solo = false;
    });
    state.songs = [...state.songs];
    state.soloSong = null;
  };
</script>

<main>
  <h1>STEM!?</h1>

  {#if Object.keys(state.songs).length === state.keys.length}
    <button on:click={() => play(0.1)}>Play</button>
  {/if}

  {#each state.keys as key}
    {#if !state.songs.find((song) => song.tag === key)}
      <div>Hang tight, pulling {key} from S3...</div>
    {/if}
  {/each}

  {#each state.songs as song}
    {@const hide = state.soloSong && song.tag != state.soloSong}
    <div class="song" style:opacity={hide ? "0.5" : "1.0"}>
      <div>{song.tag}</div>
      <input
        disabled={hide}
        type="range"
        min="0"
        max="1"
        step="0.01"
        on:input={(e) => setSlider(e, song)}
      />
      {#if song.solo}
        <button on:click={() => resetGains()}>Unsolo</button>
      {:else}
        <button disabled={hide} on:click={() => setSolo(song)}>Solo</button>
      {/if}
    </div>
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

  .song {
    display: flex;
    flex-direction: row;
    align-items: center;
    gap: 1em;
  }
</style>
