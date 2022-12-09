(*
    Here is a sample input:

    ```
        [D]
    [N] [C]
    [Z] [M] [P]
     1   2   3

    move 1 from 2 to 1
    move 3 from 1 to 3
    move 2 from 2 to 1
    move 1 from 1 to 2
    ```

*)

let split (sep: string) (body: string) = body.Split sep |> Seq.ofArray
let removeEmpty: seq<string> -> seq<string> = Seq.filter (fun s -> s.Trim().Length > 0)

let text: seq<string> = stdin.ReadToEnd() |> split "\n" |> removeEmpty
let textCrates: seq<string> = text |> Seq.takeWhile (fun s -> s.StartsWith "move" |> not) |> removeEmpty
let textMoves: seq<string> = text |> Seq.skipWhile (fun s -> s.StartsWith "move" |> not) |> removeEmpty

let initializeCrates(): char array array =
    let maxHeight = textCrates |> Seq.takeWhile (fun s -> s.TrimStart().StartsWith "[") |> Seq.length
    let n = Seq.item maxHeight textCrates |> split "   " |> Seq.length
    let xss = textCrates |> Seq.map (fun s -> s.ToCharArray()) |> Seq.toArray
    [|
      for j = 0 to (n - 1) do
        [|
          for i = 0 to (maxHeight - 1) do
            let k = 4 * j + 1
            if k < xss[i].Length && xss[i][k] <> ' ' then
              yield xss[i][k]
        |]
    |]

let parseMove = split " " >> Seq.toArray >> (fun arr -> (int arr[1], int arr[3], int arr[5]))
let moves = textMoves |> Seq.map parseMove
let getTops = Array.map Array.head >> System.String

let updateState (op: char array -> char array) ((n, x, y): int * int * int) (crates: char array array) =
  let i = x - 1
  let j = y - 1
  crates[j] <- Array.append (op crates.[i].[..(n - 1)]) crates[j]
  crates[i] <- crates[i][n..]

let crates = initializeCrates()
crates |> printfn "crates (initial): %A"
moves |> printfn "moves: %A"

for move in moves do
  updateState (Array.rev) move crates
  // crates |> printfn "crates   : %A"
getTops crates |> printfn "Part 1 result: %A"



let cratesNew = initializeCrates()
for move in moves do
  updateState (fun x -> x) move cratesNew
  // cratesNew |> printfn "cratesNew   : %A"
getTops cratesNew |> printfn "Part 2 result: %A"

