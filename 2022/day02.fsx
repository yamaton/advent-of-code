(*
    Here is a sample input:

    ```
    A Y
    B X
    C Z
    ```


    To run this script agaist input file,

    ```shell
    dotnet fsi day02.fsx < day02.txt
    ```

*)

let split (sep: string) (value: string) = value.Split sep
let inline (%!) a b = (a % b + b) % b
let parse (text: string) =
    seq {
        for s in split "\n" text do
            let ss = s.Trim()
            if ss.Length > 0 then
                let xs = split " " ss
                if xs.Length = 2 then
                    yield (int xs[0], int xs[1])
    }
let replaceString (oldValue:string) (newValue:string) (message:string) = message.Replace(oldValue, newValue)
let modify = replaceString "X" "0" >> replaceString "Y" "1" >> replaceString "Z" "2" >> replaceString "A" "0" >> replaceString "B" "1" >> replaceString "C" "2"
let winScore (pair: int * int): int =
    match pair with
    | (x, y) when y = (x + 1) % 3 -> 6
    | (x, y) when y = x -> 3
    | otherwise -> 0
let handScore y = y + 1
let point pair = winScore pair + handScore (snd pair)
let pointMod pair =
    match pair with
    | (x, 0) -> 0 + handScore ((x - 1) %! 3) // losing
    | (x, 1) -> 3 + handScore x             // draw
    | (x, 2) -> 6 + handScore ((x + 1) % 3) // winning
    | otherwise -> 0

let text = stdin.ReadToEnd() |> modify


text
|> parse
|> Seq.map point
|> Seq.sum
|> printfn "total score (Part 1): %i"


text
|> parse
|> Seq.map pointMod
|> Seq.sum
|> printfn "total score (Part 2): %i"
