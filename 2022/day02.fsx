(*
    Here is a sample input:

    ```
    A Y
    B X
    C Z
    ```

*)

let split (sep: string) (value: string) = value.Split sep
let parse (text: string) =
    seq {
        for s in split "\n" text do
            let ss = s.Trim()
            if ss.Length > 0 then
                let xs = split " " ss
                if xs.Length = 2 then
                    yield (xs |> Seq.item 0 |> int, xs |> Seq.item 1 |> int)
    }
let replaceString (oldValue:string) (newValue:string) (message:string) = message.Replace(oldValue, newValue)
let modify = replaceString "X" "0" >> replaceString "Y" "1" >> replaceString "Z" "2" >> replaceString "A" "0" >> replaceString "B" "1" >> replaceString "C" "2"
let winPoint (pair: int * int): int =
    match pair with
    | (x, y) when y = (x + 1) % 3 -> 6
    | (x, y) when y = x -> 3
    | otherwise -> 0
let handPointSolo y = y + 1
let handPoint (x, y) = handPointSolo y
let point pair = winPoint pair + handPoint pair
let pointMod pair =
    match pair with
    | (x, 0) -> 0 + handPointSolo ((x - 1) % 3) // losing
    | (x, 1) -> 3 + handPointSolo x             // draw
    | (x, 2) -> 6 + handPointSolo ((x + 1) % 3) // winning
    | otherwise -> 0

let text = stdin.ReadToEnd() |> modify


text
|> parse
|> Seq.map point
|> Seq.sum
|> printfn "total score: %i"


text
|> parse
|> Seq.map pointMod
|> Seq.sum
|> printfn "total score (new strategy guide): %i"

