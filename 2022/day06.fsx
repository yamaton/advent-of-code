(*
    Here is a sample input:

    ```
    mjqjpqmgbljsphdztnvjfqwrcgsmlb
    ```

*)

// a start marker is a sequence of four characters that are all different

let isStartMarker (xs: char[]): bool =
  let n = xs.Length
  xs |> Set.ofArray |> (fun x -> x.Count = n)

let signal = stdin.ReadToEnd() |> fun s -> s.Trim().ToCharArray() |> Seq.ofArray


signal
|> Seq.windowed 4
|> Seq.findIndex isStartMarker
|> fun i -> i + 4
|> printfn "characters processed: %i"


signal
|> Seq.windowed 14
|> Seq.findIndex isStartMarker
|> fun i -> i + 14
|> printfn "characters processed: %i"
