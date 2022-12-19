(*
    Here is a sample input:

    ```
    2-4,6-8
    2-3,4-5
    5-7,7-9
    2-8,3-7
    6-6,4-6
    2-6,4-8
    ```

    To run this script agaist input file,

    ```shell
    dotnet fsi day04.fsx < day04.txt
    ```

*)

let split (sep: string) (value: string) = value.Split sep

let text =
    stdin.ReadToEnd() |> split "\n" |> Seq.filter (fun s -> s.Trim().Length > 0)

let parseRange: string -> int * int =
    split "-" >> Array.map int >> (fun xs -> (xs[0], xs[1]))

let parse: string -> (int * int) * (int * int) =
    split "," >> Array.map parseRange >> (fun xs -> (xs[0], xs[1]))

let contains (x1, y1) (x2, y2) = x1 <= x2 && y2 <= y1

let containsTheOther (range1, range2) =
    contains range1 range2 || contains range2 range1

let overlaps (x1, y1) (x2, y2) = not (y1 < x2 || y2 < x1)
let uncurry f (a, b) = f a b


text
|> Seq.map parse
|> Seq.filter containsTheOther
|> Seq.length
|> printfn "Number of pairs that one range fully contain the other (part1): %i"


text
|> Seq.map parse
|> Seq.filter (uncurry overlaps)
|> Seq.length
|> printfn "Number of pairs that one range fully contain the other (part1): %i"
