(*

  Here is a sample input:

  ```
  30373
  25512
  65332
  33549
  35390
  ```


  To run this script agaist input file,

  ```shell
  dotnet fsi day08.fsx < day08.txt
  ```

*)


let split (sep: string) (value: string) = value.Split sep
let flip (f: 'a -> 'b -> 'c) = fun b a -> f a b

let grid = stdin.ReadToEnd() |> split "\n" |> Array.map (fun s -> s.ToCharArray())
let visibility: Map<int * int, bool> =
  let v = grid.Length
  let h = grid[0].Length
  seq {
    for i = 0 to (v - 1) do
      for j = 0 to (h - 1) do
        yield (i, j), false
  } |> Map


let folder (maxSoFar: int, lastResult: bool) (x: int) =
  let maxUpdate = max maxSoFar x
  let res: bool = maxSoFar <> maxUpdate
  (maxUpdate, res)

let folderBack = flip folder
let myScanBack folder state source = Seq.scanBack folder source state

let visibility1D (xs: int[]) =
  let fromLeft = xs |> Seq.scan folder (-1, false) |> Seq.map snd
  let fromRight = xs |> myScanBack (flip folder) (-1, false) |> Seq.map snd
  Seq.map2 (fun a b -> a || b) fromLeft fromRight
