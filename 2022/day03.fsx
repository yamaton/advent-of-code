(*
    Here is a sample input:

    ```
    vJrwpWtwJgWrhcsFMMfFFhFp
    jqHRNqRjqzjGDLGLrsFMfFZSrLrFZsSL
    PmmdzqPrVvPwwTWBwg
    wMqvLMZHhHMvwLHjbvcjnnSBnvTQFn
    ttgJtRGJQctTZtZT
    CrZsJsPPZsGzwwsLwLmpwMDw
    ```

    To run this script agaist input file,

    ```shell
    dotnet fsi day02.fsx < day02.txt
    ```

*)

let split (sep: string) (value: string) = value.Split sep
let text = stdin.ReadToEnd() |> split "\n" |> Seq.filter (fun s -> s.Trim().Length > 0)
let halfAndHalf (s: string) =
    let n = s.Length / 2
    (s[0..(n-1)], s[n..])
let findDuplicateChar (a: string, b: string) =
    let xs: Set<char> = a.ToCharArray() |> Set.ofArray
    let ys: Set<char> = b.ToCharArray() |> Set.ofArray
    Set.intersect xs ys |> Seq.head
let charToInt (c: char) =
    match (int c) with
    | n when (int 'a') <= n && n <= (int 'z') -> n - int 'a' + 1
    | n when (int 'A') <= n && n <= (int 'Z') -> n - int 'A' + 27
    | otherwise -> 0




text
|> Seq.map (halfAndHalf >> findDuplicateChar >> charToInt)
|> Seq.sum
|> printfn "Sum of the priorities of item types (part 1): %i"


text
|> Seq.map (fun s -> s.ToCharArray() |> Set.ofArray)
|> Seq.chunkBySize 3
|> Seq.map (fun xs -> Array.reduce Set.intersect xs)
|> Seq.map (Seq.head >> charToInt)
|> Seq.sum
|> printfn "Sum of the priorities of item types (part 2): %i"
