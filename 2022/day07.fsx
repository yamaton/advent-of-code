(*

  Here is a sample input:

  ```
  $ cd /
  $ ls
  dir a
  14848514 b.txt
  8504156 c.dat
  dir d
  $ cd a
  $ ls
  dir e
  29116 f
  2557 g
  62596 h.lst
  $ cd e
  $ ls
  584 i
  $ cd ..
  $ cd ..
  $ cd d
  $ ls
  4060174 j
  8033020 d.log
  5626152 d.ext
  7214296 k
  ```

*)

// directory and file as a node pointing parent and children nodes
type Node =
    | Root of children: Node list
    | Directory of name: string * children: Node list
    | File of name: string * size: int
let breadcrumb: Map<Node, Node> = Map.empty
let getRoot() = Root( children = [] )
let addDirectoy (node: Node) (name: string) =
  let newdir = Directory(name = name, children = [])
  match node with
  | Root(children = ch) -> Root (children = newdir :: ch)
  | Directory(name = n; children = ch) -> Directory (name = n, children = newdir :: ch)

let addFile (node: Node) (name: string) (size: int) =
  let newfile = File(name = name, size = size)
  match node with
  | Root(children = ch) -> Root (children = newfile :: ch)
  | Directory(name = n; children = ch) -> Directory (name = n, children = newfile :: ch)

let moveToChild (node: Node) (name: string) =
  let hasName (name: string) (node: Node) =
        match node with
        | Root (ch) -> false
        | Directory (name = n) -> name = n
        | File (name = n) -> name = n
  match node with
  | Root(children = ch) -> List.find (hasName name) ch
  | Directory (children = ch) ->  List.find (hasName name) ch

let moveToParent (node: Node) = breadcrumb.Item node



// let filesystem = Root (children =
//                     [
//                       Directory (name = "a", children =
//                         [
//                           Directory (name = "e", children =
//                             [
//                               File (name = "i", size = 584)
//                             ]);
//                           File (name = "f", size = 29116);
//                           File (name = "g", size = 2557);
//                           File (name = "h.lst", size = 62596);
//                         ]);
//                       File (name = "b.txt", size = 14848514);
//                       File (name = "c.dat", size = 8504156);
//                       Directory (name = "d", children =
//                           [
//                             File (name = "j", size = 4060174);
//                             File (name = "d.log", size = 8033020);
//                             File (name = "d.ext", size = 5626152);
//                             File (name = "k", size = 7214296);
//                           ]
//                       );
//                     ]
//                   )

// filesystem |> printfn "%A"