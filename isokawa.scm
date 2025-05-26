; for partial application
(define-syntax pa$
    (syntax-rules ()
        ((_ f arg ...) (lambda (x) (f arg ... x)))))

(define (1+ x) (+ x 1))

(define (1- x) (- x 1))

; A list of integer between m and n (m <= n)
(define (range+ m n)
    (if (> m n)
        `()
        (cons m (range+ (1+ m) n))))

; A list of integer between m and n (m >= n)
(define (range- m n)
    (if (< m n)
        `()
        (cons m (range- (1- m) n))))

; sum :: [Integer] -> Integer
(define (sum xs) (apply + xs))

; concat :: [[a]] -> [a]
; e.g. [ [1,2], [3,4,5], [], [6] ] -> [1,2,3,4,5,6]
(define (concat xss)
    (if (null? xss)
        `()
        (append (car xss) (concat (cdr xss)))))

; tails :: [a] -> [[a]]
; e.g. [1,2,3,4,5] -> [ [1,2,3,4,5], [2,3,4,5], [3,4,5], [4,5], [5] ]
(define (tails xs)
    (if (null? xs)
        `()
        (cons xs (tails (cdr xs)))))

; fmap :: (a -> b) -> [a] -> [b]
(define fmap map)

; return :: a -> [a]
(define (return x)
    (cons x `()))

; (>>=) :: [a] -> (a -> [b]) -> [b]
(define (>>= xs f)
    (if (null? xs)
        `()
        (concat (map f xs))))

; e.g. (split prime? `(2 11 7 1 9)) -> ( (2 11 7) (1 9) )
(define (split p xs)
    (letrec ((recfn (lambda (p xs acc)
        (if (null? xs)
            (list (reverse acc) `())
            (let ((x (car xs)) (xs` (cdr xs)))
                (if (p x)
                    (recfn p xs` (cons x acc))
                    (list (reverse acc) xs)))))))
    (recfn p xs `())))

; e.g. (pack `(1 1 2 2 2 2 3)) -> ( (1 1) (2 2 2 2) (3) )
(define (pack xs)
    (if (null? xs)
        `()
        (let* ((ys/zs (split (pa$ eqv? (car xs)) xs))
                (ys (car ys/zs))
                (zs (cadr ys/zs)))
            (cons ys (pack zs)))))

; e.g. (encode `(1 1 2 2 2 2 3)) -> ( (2 . 1) (4 . 2) (1 . 3) )
(define (encode xs)
    (map (lambda (xs) (cons (length xs) (car xs))) (pack xs)))

; A list of list of integer, the sum of elements is equal to given
; e.g. (split-number 3) -> ( (3) (1 2) (1 1 1) )
(define (split-number n)
    (letrec ((recfn (lambda (i j)
        (if (zero? i)
            `(())
            (>>= (range- i j) (lambda (x)
                (fmap (pa$ cons x) (recfn (- i x) x))))))))
    (recfn n 1)))

; e.g. (combinations 3 `(1 2 3))
;   -> ( (1 1 1) (1 1 2) (1 1 3) (1 2 2) (1 2 3)
;        (1 3 3) (2 2 2) (2 2 3) (2 3 3) (3 3 3) )
(define (combinations n xs)
    (if (zero? n)
        `(())
        (>>= (tails xs) (lambda (ys)
            (fmap (pa$ cons (car ys)) (combinations (1- n) ys))))))

; e.g. (cartesian-product `( (1 2 3) (4 5) ))
;   -> ( (1 4) (1 5) (2 4) (2 5) (3 4) (3 5) )
(define (cartesian-product xss)
    (if (null? xss)
        `(())
        (>>= (car xss) (lambda (x)
            (fmap (pa$ cons x) (cartesian-product (cdr xss)))))))

; conjugate :: Circuit -> Circuit
; Find a conjugate of a circuit
(define (conjugate c)
    (case (car c)
        (`r c)
        (`s (apply Par (map conjugate (cdr c))))
        (`p (apply Ser (map conjugate (cdr c))))))

; resistance :: Circuit -> Double
; Calculate a resistance of a circuit
(define (resistance c)
    (case (car c)
        (`r (cadr c))
        (`s (sum (map resistance (cdr c))))
        (`p (/ 1 (sum (map (pa$ / 1) (map resistance (cdr c))))))))

; Circuit = Res Double | Ser [Circuit] | Par [Circuit]

(define (Res . v)
    (cons `r v))

(define (Ser . cs)
    (cons `s cs))

(define (Par . cs)
    (cons `p cs))

; circuits :: Integer -> [Circuit]
; A list of a circuit containing n resistances
(define (circuits n)
    (define (template series/parallel Par/Ser n)
        (if (= n 1)
            (return (Res))
            (>>= (cdr (split-number n)) (lambda (ns)
                (let* ((f (lambda (xs)
                        (combinations (car xs) (series/parallel (cdr xs)))))
                    (as (map f (encode ns)))
                    (bs (cartesian-product as))
                    (cs (map concat bs)))
                (fmap Par/Ser cs))))))

(define series (pa$ template parallel (pa$ apply Ser)))
(define parallel (pa$ template series (pa$ apply Par)))

(cond
    ((= n 0) `())
    ((= n 1) (return (Res)))
    (else (let* ((ss (series n))
            (ps (map conjugate ss)))
        (append ss ps)))))

(for-each (lambda (n)
    (for-each (lambda (x)
        (print x)
    ) (circuits n))
) `(1 2 3 4 5 6 7))
