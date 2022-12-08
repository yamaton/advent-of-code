(*

Here is a sample input text:

```
1000
2000
3000

4000

5000
6000

7000
8000
9000

10000
```

*)

let split (sep: string) (value: string) = value.Split sep
let parseChunk = split "\n" >> Seq.filter (fun x -> x.Trim().Length > 0) >> Seq.map int
let parse: string -> seq<seq<int>> = split "\n\n" >> Seq.map parseChunk
let text: string = stdin.ReadToEnd()


text
|> parse
|> Seq.map Seq.sum
|> Seq.max
|> printfn "How many total Calories is that Elf carrying?: %i"


text
|> parse
|> Seq.map Seq.sum
|> Seq.sortDescending
|> Seq.take 3
|> Seq.sum
|> printfn "How many Calories are the top three Elves carrying in total?: %i"
