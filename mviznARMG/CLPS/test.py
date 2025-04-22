import tkinter as tk
import subprocess
from PIL import Image, ImageTk
import base64
import io

# Base64 encoded logo placeholder
base64_logo = """
  /9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAMCAgMCAgMDAwMEAwMEBQgFBQQEBQoHBwYIDAoMDAsKCwsNDhIQDQ4RDgsLEBYQERMUFRUVDA8XGBYUGBIUFRT/2wBDAQMEBAUEBQkFBQkUDQsNFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBT/wgARCADIAMgDASIAAhEBAxEB/8QAHQABAAIDAAMBAAAAAAAAAAAAAAcIBQYJAQMEAv/EABQBAQAAAAAAAAAAAAAAAAAAAAD/2gAMAwEAAhADEAAAAbUgAAH5P0huVT7zUzbECawWiVe2wnVhc0AAAAAAGIp4T/XfJWzNC/MBaAZWMLkzCc3fz1L/ACcr3SKKynM6abGp0l2/lraUtK9XtAAAEd63SEztjvVYw+WjeZtkRbM2x1ZLI17rNnCxU5UCwJ0gytcrGiGplHNfU+odNDXbx8xtwOkjU9sAEH5ihZ+ZkhzpGbRUWYttPq2MK8wBP1WizlkPHk8VZtP6iiE+U6ugTaB48irtTuqVcisHQDmxt50lYEa/z+6fxgUFvZRn5zqWgeeACsFZrjwAXq91Qban0/N66iEEXDhawBMoEIfVgyWokmfnOa9uXo6AH3M2AI1of06085uWah/RDqZ9HOm4ZKdTLZ4k57YrpVW8rj6LhyuQZYj48cZ2vsU5c99sPmo2ejCbjdUxmzAAAB8VTLgDlf8AjotVkwM8069B0X2vl6OnWh0ByZP0ITZZYiqTIZ1cj6fpn2M8eQAAAAAAwsXzUK6fTYIRbJH1Bqe2DU9sAAAAAAAAAAAAAAAAAAAR+SAq3iC3aBtFLZ1dlnUicvZEMuledpgqy5j5MjfXCa1bdeLZovjEs8qHY424AACIJfiAxEg6hu5Aloa4WWKgW0qPcMpvPMKYIlPbJHjgxs1Qr9ZrGy6rYsgrK4raDYYRneAi0AAAGgb+I92TPCHJjCv1gQ0WH7NBou9COYWteK25eexGOb3MYiLJqAAAAAAAAAAAAAAAH//EACsQAAICAgIBAgYBBQEAAAAAAAUGBAcBAwACECA2ERQVFjAxUBIhJTQ1YP/aAAgBAQABBQL+A7dsdOp61AwbMCZ1IQuFGsQF5MuYLozsvHV8dd46vjAuIHKyNNQTGv8AM1WSMW+fOM9ny1Wthi3hossWu5P2MaPZ/fOkbbs530bNXnRI2xdq7bxIblfaxrNp/EULRAsNwtSYa4kVduM87dh60Lc7SlGsr6UWZshaYHxsQFYQLxjrjrjvr67MTk0IS4XpkZKwwV8ZXfEaVuh7063cd869nTdr9bc7QlKMwMk9om17WWI2DRuIvjz7EVsIuo1JFH4Lmx61BGFIpiHbzPKF7qhZpJbWXMwwUMaUimInhprAYfwwq5BZk8TLAmKu0OZiHoPpfbD0rGubN3kZVXoGNXQmSjh4MveWtZhVlGCqQ+XYIznoIYSIHOteYmbv3BsSr3MHp57dSwvtHD+SA6MViu9YyAPhZaZqrPWmaG0D/Nh2D0W9O7d3kbayT/uMp/bp1PzZloMYEBEXB/Gu1/t445vkpw7VvXeiLD5nHxxZte6dcZOsiUpw0qzMtRfz++P9X42Yzj4ZXmGWtEVlliNI3lgO3RTgSJGyXv06e8jcrgta4EsPuUkwVhbjK4vw/wBaxSGpXgdSbF+vO3V136ikL5Esj1tHWu3o/fLJrzTO0cWGaUrEwhqKwDXFSjtowmMkh50SVtgyUR/0NWj0WDZvy/YGQ+lGdO3pv1eJMjXEjkp2Z5RDszDFu8v7hshZWhGQIO32XA8RxVV5TUTDB4wEdx4SNDbCID5AqZHk7Ye9DsrSf6+WOq4jEafa/wCyjiubJ1jNEeTql6pc3RA02NZHQ1pS6y3NEJQrWOpkvD8/6lePWihtjcNF44EafNb2EqtrcxoIri5EWBvl0SIrdELh5YKdjP8ATlJtjtGxoka5WnxdpPbmQBTirJrkayS7MHiy7XuOLhBc30uS2yAnh7s/SHxXSLtMypUrVBjvztsbJ6ooTWyavr0NaH+lmVoLVCak6eqSuLDqSVdqxYopkxwmJiGYsWLphR7TSp5snVixJXRJIXEMRIkPRAjlzkEDGcLVlmsV9Wfaf2nT4oeE9P8Ava96TWspjyNGxhEP1zIWghGb6j3RM7NfbT34Ask0BwLugZIxBfABDnQlE2Y3mx0XBKz14dg5c8yTj/JtBJKqvSIyzuA9UjGTxmwiidU2gbzGPhj8TGkimfqwVKWFZ3aNkfZ6IIyWU2r1NzZeRwgQnD2a287e4OrSrBICL0BejfmIhYBfpMqJfldu1Ji/jppYP0zBrNdgZjRNMPXxlWojSPCKotd6f+ccmsypufTv129OWo5TAOw6JLkq9rwVODLf5Xs1JXlodYxs2NJHntU5Ks35sWUn2EH0Irf1bxVvg/qK7Vpv6wq5z8MC8fflnPBmQAWK/PSmNdZJbpqMfP2PwFYTFMabEYZayAiWEcPjiR17VOKrFpaQ3qtf2RTsHXHVnXR1kKVIQdeeu/T1kaaU756GpcXXNi1zJ2KzxY5v6GqU2D+SCWn7GqH2byynntB5XiP1V4Vye0qpga4ia2x+kpYo/bnI/wBVr+yKl9lt3tWkP+Zyl/cXLcG7BJ59P/exYdB1jIFp+xqh9m2E8dFaDWiR3jeLk9pVr7IZPbtHf6vqegkhiW0MFJXFw9C2EgdbKk1UhcrpHIq5bjqvfc6+hVnOAnuO4aQwLKCAkra8w1wfIs/0mxOCBj1rJ2EuymcCnCd4JaMRe84TWijOU9P8r//EABQRAQAAAAAAAAAAAAAAAAAAAHD/2gAIAQMBAT8BKf/EABQRAQAAAAAAAAAAAAAAAAAAAHD/2gAIAQIBAT8BKf/EAEkQAAEDAQQFBgoGBwgDAAAAAAIBAwQABRESMRMhIkFREBQyYXHRICNCQ1KBkaGxwTBicnOy4RUkM1NjdIIGNVCSs8LS8GCDov/aAAgBAQAGPwL/AABVVbkTetK2ya2hITyWOj/mpiSCEIughohJcqcipMnstGnkYry9iUqMNSpPWgoKe9a2LJNU+s9+VbdkmifVev8AlSI+MiGvEwvT3VjhS2pKfwyvu+nJkF57NTzLS6h+0tK0CqENF2kHZZDt40Lpjz2annnU1D9lN1EyC8+mJ5ppdQ9q0QrI5rHXzMfZ9q5rybDRl2DW22Q9qcqOsuE04ORAtypQt2iP6QY9LJxPXvrHCkIRp0mS1GPq+jKTMeFhkd5fKjjWdihQssXnD7qCbamKPDXWLWRu9yVeuihQmE7ESji2apQ4OSnk453JSLFjqjO993ZD8/VSFaMhyY56AbAd9Jzazo7d3lYL19q1qS6riFCTgqUqv2ZHJfSEMK+6lKBIdhH6JbYd9EbsfnEdPPsbQ+vhyA8w4TLoaxMFuVKCJbmpcklimr+pPnQm2SGBJehCt6L9B41dNLJPFxxXWvWvBK08xxT9BoeiHUiU3aVrt4nuk1FLyOsuvqpyZMc0bQ7t5LwSgZaaMgv8TEb3da99BJtfDLk5own7MO+tNLdCOymoRTNepEoJUN4X2TyIagQoMpyM4qK64rRXLdknzqfEmyXJDzao6BOleuHJfl7aKVNeFlpOOa9SUEmG8L7JZEPKT0dEgTF8ttNku1K0U1nCi9B0dYH2LyI0V8mz1XaYVej1jQS4TqOtF7UXgvhLFi4X7TJMtzXWvdTkiS6Tzzi3kZb6btm0W/GLtR2S8n66/KnZcpxG2GkvVawMCrcVvoovQZHivXWijBieL9o+XSP8uSBaY5JewfxT504sCWcbSJcWHfXOuaS5il553f61rnXNpcFU883l7UoXZ8k5BilyYsk9VS5xX/rDmEE6h3+1fd4BxpbIvsnmB0cyz8UmBmQ5m13pyJIileC/tGV6JpSSoha8nGl6QLwXwFhQiQ7SNM9zKcV66N101ccNbyIl1qtc6khfAireSL5wtw1wRKSzLOLDZUZdp3yftr8qCJDbwgnSJczXivI/AZgjKRm5CNXMO1wypkSb5rGa16ESvvLjTNqWkyjspxMbTRpqbTct3HkuWnLXsxpGlDXIYDK70kpyLoEmMKuIBI8ODjRQXogRVVtSBRO+9U3eC5aNjN3H0nYg7+se6rl1LQS4h3KmogXomnBaGXFW5cnGlzAuHIgNXHaD6eKH0frLRvPGrjpriIyzVaBpscThkgiKb1qNBC68BvMvSLetRrLsxk1OeejcfTotjvv/AO8aCJHS9c3Hd5lx5Zdqwz5rKESddFeg5vXsWrOiua23HxQk6r9fgG2aYgNMKou9KlxE8y8TXsW6m5so+c2jdqVOg32cfCfteBhYktipvBkLib17eQZUZbxycaXIx4U1NiHiaPdvFeC0rLlzckNbL3or3U7Eltq0+2tyotNSGCwPNEhgXBaRh7CxaQJtN7j6x8GZY8Bnb2mXnnUy3KiJ86hTNzDwmvYi0DjZIQGmISTenK6+6WBpsVMiXciVKmZK88TvtW+m7OmtaOeqbJtpsHcnu8ALFsrxtrStjY80i/OokEnSeNodoyW/X3UNmNF+sS+ndub/AD7+QYsdMIJrde3ANNQogYGm09arxXkvS5qe2ninv9q9VORZTSsvtrcQlQPMuE06C3iYrcqLQQrQIWLRyQshe/Pq8B60CmOR1duxNgCZ3XX0w+w4ciG5sqZ5idBZdqndHHUzI9DqXqpHWHQebXIwK9FpXZLwMNJmbhXJRWZZirzS/wAa/lpOpOqimSH1hRl1NLhxKfH1UU1JZSnMGAUIMOHlWNGUXbTNNQ7mute6it21MR2hJ2g0mYou/tWnpsosLTaetV4JT86Qu24uofRTclDFiD1m4vRBOK0ESKPWbi9Iy4r4Gu5mcCeKfu9y9VHEmNK08PsXrSr01LQQraJXGsgl5qP2uPbQOsuC60aXiYLei8sCAgkjIoryldqIsvd86dcgxsbbflkuFFXgnXRxnFfgyB6QoSj8KIY4PzzDpKR34fWtI1PjqypaxLMV7FqTEMC0cdy9s1TVcuaf948rkGyyF+dkTuYtd60luWwhONqWNsHc3S9JeqnH33BaZbTERlkiVhavCz2V8UHpfWWtHHHAwP7WQSbIfnQxIYYRzI16RrxXwtBLDbT9m8PSBawSAxxyXxcgOiXcvJ+rOaSOq7Udzor3ULek5pMXzDy59i7+RY81gJDK+SVAww2LLIJcIAlyJUWZZsZZBK3o3UFUS67L4+6pSzWdBKfd6Kr5KJq+K0UaYwMhkvJKgYjtCyyCXCAJciUr86QDAbr8y7E30cWzcUKGupT84fdTdpWu2oxuk3HLNzrXqo5ElwI8dpM1yStAziYs0F2W959ZUEqXiiWdnf5TnZ303FiMiwwGQj9AceS0LzJ6iA0vRaOVY18hnNYy9MezjSgYqBjqUSS5U5BBH+dx081I2vYudIk6M9EPiHjB768VajCLwdXAvvq8JTJJxRxKvenxmk+s6KUv65zo/Rjji9+VE3ZkYYg/vXdo/ZknvpEvftCY5/Uv5JQTLVwyZiaxZzBvvWsUlzE+qbEcOmXdQtC2bmvxUVnoh/3jQSrXwypOaMebDt41cmpPo1WUxgkbpDWo/wA6JyHdaMf+HqP/AC91K262TRpmJpcqeDookZ2SfBsb6F21Xkhtfum9o1+SUWhBqGyibbxrrXtKlhf2faJ50tnnCjf/AJRrntuPnHE1xEhriePurQwY4spvLyi7V+nwzYjMlP4gXqlKoA/F+6c1e++tmdLTtw91eMlS3P6hT5UipAR8uL5KXuypG2GQYbTyWxwpyJEl4kFDQ0IM0q6DEBst7i6zX1/+OsoUsispxRd0WAeh5SX3dtCYriEkvRU5IUOzX9DJO9xwkRFXDkia/X7K5niKVa7gNqWtAXFiRV4JqoI1ogrclHCW5TQtXan00ibEw6cCBExpemsrqYiWZFGXbJ4idNBuBob9VBLtBRdjKty3iBB2Lh1pUH9Dxed2tMTVGz0V2d9FPkEmgDWYgLZIKdaJSukCNSmVwvAOXUqUMwBvdhFi/oXUvypkCK96J4guzyfd8KvWikrtxGnNJ/6w6Pt1e2pc6Lh07eDDjS9NZonzoJkzBplcIdhLk1U8Njw2XbP2cBGoX5a8y41/d0b2t/8AOotlyUjre/o3RaBCuTfrRaGXCwaVXhDbG9LrlqLEseIMm1FDFJfw3A1rW7PVlQy7QUXY1+u8QIOxcOtKanNJgVdlxv0C3p4cz7bf40pZCJ42Q8WIupNSVa4ml6JGM/WiXp8KtOYqXuootCvBM1+VONGl4GKiqdVWm0nRVlF9hfnT0d1MTToKBJ1LUuxpC3C8qs/1D0V+PtqUQlc8/wCIb9efuvp60THxksrh+wP531aPa3/qDTf3x8n6FstVOe9suE3mF+5PrLWnkIhWk8m2v7tPRSg/mQ+BVFdAduQROGvHXd8qtVs0vHmxr7Evq1G/JF0C9qL3eHM+23+NKj/eOfiq2P5N38C1af3w/DktL7j/AHJyQLbjbJHdeSbnAy93wqx4MFcQkAav4h3fDV76jxGkubZBAT1VaPa3/qDTf3x1oI6oVpPJsD6Cektfpy1EU5z220LmY3+UvWvIH8yHwKrL+yX4yq1P5V38K1a/22/93hyIMXBpjIVTGtyaivpqFLwaYTJV0a3prWrQiNXaV+ObY4sr1G6pjU3RYnXEIdEV+7kmSZis6N1rAOjO/wAq/kfhhhR/UbSlkhJQzrRVlRaBdGjZX7S/lfyS4EXBp3cF2Nbk1Ei/KghS8GmRwi8Wt6a6lWnHcjKhO42ldO+5N2pUr+9Y3/z/AMKilOtJhyGjiaUBw3qO/wAmhiQ8GlR4T8YtyXXL31CgycOmZRULAt6dJVqbGbu0jzBtjfxUbqnjO0V7xAo6Ir8r/wDFv//EACoQAQABAwMDBAIDAQEBAAAAAAERACExQVFhcZGhEIGx8CDBMNHx4VBg/9oACAEBAAE/If8AwADGlSAKtHMnIPOHaagrmGSTCb+jmRT93NNhTCz5PFA6sCPzpPVIf00zQaLvtfFaklYV1GT3/n0SZkHh6Xa1D0M/LL4u0E26yDs9V2satRpu2dCWlz6xRH0L0qlWV1aDkHma8weerq+lfpEoJh2nbeHu71DEE9zv2Lfx5B8Nl2GrwUpL1xYPlMeDvR59qi3fky+aR7DbL9r3auzIBg8vgPfanrt0T7/2Vqbl/uO5Rg/hD5RqIANgpK6bop5O58ii1oiCvzftRnLNA4Z9x6MnqRo4SoFHiGLpY6O2tGl5CBuP8E8uN9aDPapaSYtC+qctDfSBbbC18Gt8EwDAOkLVathjvQ+R3WOKxIK4Jzv8daADWGw6PPtQKSuMcJo8NPYr62DJ08aZoyCdYl0Eo1Db5OxleCiK3cY4TR4fRJKvi2z773IetSfu0A+ls+i76+LkaPGHzW3Bbqg0fyT+wMyfLt9MoRkyqpxdlcNA3/62iW8n/BuuAqYkvPbq/OCxQ6FiPe/XA9CxVdmTf+9qsWK2J7G085qzCLSwOM50q0GYZYGzZjrQ+V2wHAsfunnITW16YcofgAj0Ek68PJUbz7Ac/J339LQMDeiednSrHlcejPh1/C4o/kj/AAHu8pwpNFZVo1hYBbL0NX2NaViobLYClPTMd2juah/tjN8vVVtX0QGxFuEsJYk80E8EIvcsE2sbX3oYSpM/Jqeb460EEFAwCNkat/BiHqPSNTa/W5+98uyzZtb+6cixm2TcGkvt+CARJHSs60BtvHf/ABtSMCFkdK8/ZMw+xWqZA65+nX0kJJLcOHiNDV96STtSVZWnfZpCMBQ+qItW/e8BThxlYMhaSTfYpr/nHOX6ND1DjJJYBT2NLca0XnJVeHYaAABAaHqUdXDIQlSymGXl/SjADc0lITchSXt+IgkZHWhUYOwBPDHv19JttfOufp0qMBbrqC0SrsQx77butSt9KJtk3HelKkDoMjSc5LwP2k0/GSFjY6RuLq7a1YqQY1Ap2mhaNwCEj6mywZAStQQsk6K/tSW0r5dGTXA8dMfg8asuS/Aemxfao4aUJO7E6FgNqgb3Qrk37iOh6EcQmE7552NasSU8pNV9LnfWs/KvHeYxUC88nNEePGi1GiHAl9ht5tNvwJCMyEBcXWDSrZ9sC6YY0THRpPF4Lw+4dOmD8HIXvCgm7IBe7UgPujDofLXplr0Qzc3RJAxNMYzIiSS5do9/XfnjgfPt+lZ6MN2ef2DrV278ey5lrRvMbHh4CrIXD9WfrWrSYsnK/o0/DYBT/r+GlOLXDh0TUd6QEQZE0ot0jtFtd3WosgAB3E9UW9JDLAdYTVMJLi3QbNIhIy5ckyvUdo3IGJS2Ghv18Almrl6aTui7iL67jEH+t2wa7VkyEzlfZv0ylZKkAqXTyWyvndDQ96NMeYA/fCo9J5Rn2PyUwZUHXDtxhrClAvubPn0MZUdPS3cnmh8LRIS7Xy49NL6Lh3HI8lWVcoDpTHR3CEu6ZEUbGApF4x3pzqqHDuOR5KtPtEFEVeDvbZF0okpqVA8pjwd6GQ4HjY2eOvTN4i20GgHwFNLoZbv2g0oaZEGQfFwf4mhhDBvLu8v8BaeoA1cac9Tp4z1pbcXQNkoYZLNYIpuwOw7xWu9UX6fCgSRfbSj7dqp80pANfnGgAiayXh5U4NWG94oBlAIJX6HsUc0Qa65/yOc1nmpk+zo5aA24JQ3ed14pON4HdPl8daAgAsB/GbCCLC6v7TRYCuQhOdXdSOrhXqB/Eio6+PWMVlBBY4S/2UgyeLOVs01EIPk956val/eaAJ+fag/XmXfI/wA+mqBDoHJ7U4cdJew0dYu0lBCFsUJhB/0p+FYOUED2PSVHzwc2kcknvVoxwL3rv7Y/+dKjicDKM5ZNWpRkxMYjh9FGlE1oQcvgqAFnzkPmxCT2p8KdzJtcTz/Mox0RYVujWj5kV2TE8rGMzTI3QkG5CgjstpkoUYkkti12K7KbU0Jjk70YyutHsm/ZrJopM2fLL2auva7mGXge6gZIC6tOVkr8WAe7DlTbldxCt0VIkmeOVrUUnEMpjpHVp6JoTKKgHFxYm5tSBBrmitvYpIRICygSugN32dC2WS5m5DwVKBixmHU9xOE/goHfkNTCdC770XwGHd+YUMVSS9zufCgoNFhRDS3XicwHyrmbl4Q/NZ1K1hZfePDVs72szOXtJ2q0lLXkDv4D0yfR7noFYlehwi/4HLUP79fVm+XV6enoMBGu6mewKAk0N3UPcKTbYByB+H8FD77d+DTHyPpXmqNYBb1hVZ8RHBdD0Q4p7fp+In0yfR7lSo/1tKL4NXpShLi5Dczb3sctvw9ZLX2O35lpGmmivDoUgyxskheCswMdEsJdpaeVToGCF7HovLcE5hdY29Fu4L4Stfkk96mCe+8UshheHoqATdl5eipsWjwiteCrxosgYqS0Y9Okbe5h2EHTmmiLXHAbw7KnG62DYPRKyGhMEgT3palKLilNjc/9b//aAAwDAQACAAMAAAAQ8888880088888884c8AM00U8888okgY0M8M0s088gA8ss4Y88cY8sI88I4oc84w488Y88oA840kAc888Mk0MY008c888888Mss88888888888888888888444o00c4848888Mc84gU8Ac8888cc8cscssc888888888888888//EABQRAQAAAAAAAAAAAAAAAAAAAHD/2gAIAQMBAT8QKf/EABQRAQAAAAAAAAAAAAAAAAAAAHD/2gAIAQIBAT8QKf/EACcQAQACAgICAgICAwEBAAAAAAERIQAxQVFhcRCBIJEwobHB8FBg/9oACAEBAAE/EP8AwFj8MAWqtBjSkZh1n/3/ABjaH/kUlYJh9fGrHDC/4dZMlY+1QsV5I6/Rx/kwuc8Vfp/yY+bgTt+hezkXbAfsLl8A/nfNlxPj2HqPAbwDtorjEUwbE8wBoB2DK+STBwvaaxNslwR4v8oByGSG9BjXAOjcw8GO2dKkq55kMX/RiUM/9MnzN4w0u0CZGk5qdkAp6MvTIuuxvs7KcWdH+Mh78pFRLeKBXFtkeMGyre2e1MZAHKe7Akt/oagTHHk0HVAWri0eVx3Q6QBgbu6U2uEZYq2xcMVHIFgPxC1N5JJPz9GBUYP2eS/bgw9oEB9ZQBZA304FI0CWed15nHpUW8uCED3P1l7BKvaID3AeX4BjHsjkCYoEY8jR/gGOxeDOCeTJAUicn8EXDQw4Rbv5EtgWYZyyLUGrG6lTyLh4ykHmS9gq2lTFUMyKxs9Kj2qAolruW109ENwATEMgfMqdoGsXM962yPsP0gq8URQgNwXksLktLnePkBOseAmZCPQYlE8Ye0u1ChRZVHbyvC488Edvoe9Xk350vLnePkBOT4BBBGkeck0lEG/XBb7yXhkr0iWJzGC8qgch8TaAbzbV7n2IWA+7haRh25zY+EkR/K0QNQ5Ue9Xk2wRhN1Zen+AKAoAAAwdhCm7UOew6I2cHGI270XKgFqhk9AhLNYSVBli0dAQCBKj7eJ1UcyyuGMsJWxC0WBcIDoSHwxIHBISwk5OI6C3aCQCWBQTkdqIxkirMiFKGDKEyGUBREYlQlWzjsj4TEBpMi3+G39QJ0HYbEEbEwyQaK8tEKethpUsaalWjungXDa8KMCmEFWlBx0ULOQ+eMIQJUWllv+iDDwIrMJQtVd5/vkDhQP1yZnDfUAjfQBk8adSo0mzsZSWpMFWHULDyZ+ggAAPitNS8JhoAs7BxiImK35F0gQEdG2bE2qJJUCKGKVZAIACgOMCCyBInSZKzC4nQ09iplRHCXMZkcxZMstARTbHrA8WJDlaO/wCBkAQokTCjnQnINrkmno2fyKHCjYnDiYYyqyfLDw7UJCZFBYNMaUTZzoF9hidlReFHlK/oDDjvBsJQ7VwtHiSOF5VDAbCH74eZSE6BxiC8NAIBveLjEqYO0wBiz0TjQAdr8JEaulxtYTMk7CuAsq5ox9gn3htjQBAHXyAHFpRIOkUxZ8L3cauHyAZoMGlEC00Nv4GQAkDImEAo8/AWiCuiNxZxjkJKSr6U3sXZI1Lhgh9VtMJ6SRFjSCwoOC4YehLDGcZKocvQoQUiYHloRTgCIwhSRkkQQQDc2znb5F/jCGUiEivaFNHSrElrc++5ID7xFj8yaA8iI/KtZAhIr0DiEpjTRP1iey2YUcJZRy4YafgmUUtSxk0XbmcbHSbLSJ7hDgAwHkHvDnUY9g+JIDlyV9yslldAoZqOLaveK1+iAD43Y2aG2m1c2tk4YT5+KI8B0hCCRERjGlIWUSA04ZCjg408W5026PmcdlKUDiGTlLzjp11WgQCGq7J4lw3Q6XeO4LTPBoOAkaNU8iI4nyQPvYGLPCkFJI6EmCqGIQSxOpkMxAqYEOTMayT2uMIaTKdFL53RnYSo/C23t7EiDmtvl2C+1jkAy0mElUR3GA8y0Lm1hGGq9UHllbXHEwhZfsH9bKjmNdMLUoV/RoID8J7OZIJtgLd+0zyHR+kz6L8YetiYd8ScKNI8OVKQFFoAvwKcmwVbDFukET18pg6OYqCELYahOPWr511nKga5SSZf/hyAkwBERFGcC+jcQ0UXKiXh6wvGQIeBRaxMIMnPGRXshqWAwrJM0+YAXUjtIbC+xyTDEvLrzPIS2HcnTB0DBlLV/wBc6MAk+65odVchG1M8RoHompjRZdsEoZOAOMSHnrwaFAH5QxoHDj2lUvR2CJlMKUNgvRu6mIX8b+Ot30b9bxIKwAKCN6a/CEeD4Sekst4jQLsHzhJwjR+Af8483lEpzc0adPGBM2RwE1i0RPOcwef6BQLhBO8MvQmB0HPK7W3Bho2YOHPgBzxCRW8bD2K8wUx8qLnLG3oRXzjAMxJ4QQNtaBSsAZeM5QK1FzzaeTeQ+q8Hbce5HS0UpIiJ5TabUVdv8CsthwenSbEsbMfW3Hntm0cLrvjXmoAKUWJ04hIgyJswJ0YRBcSlOiQ6xAPAiB5ZIPU81bcKm6gz+sHD0i0ezBBIl/w1xHAWH66Fjl40AY8AT3hNwUxWfNB9B0ZFaQRsxlQdxJoQYWGQHI4fJ3EbiWslNXxgOMYcPnSs99Yvgtr6SPVHDkiBQAaA/j1kFavVEA6PhGSilT38LL2T0ZNgMhugCPv8WsGEy8oIHlgxjHgs3Rn238GBGdAi5GV0TFwBrFVOSiVEcvQ/feATdYB5EHGyajj5uEZGcu32wcB/PVT/ALFGfYjJIcM8H/ghyVdBH/cMGjNkX9J/vIyBobfchgK0R6uhD4aZre2jIEKkjUthhRP9vK3B6J4f/Ooc/cQC7KBsG3HHSFIwg9Ij8T5uFwgAb+p9mPUAWOrtAO4k5rY56e4S9mBrT+ZyyBUySRNnOKtwvIboRYDSTRQJ1zSa0BJ0MhNC6wwvaS0T5AjYImBDB2XfiSEfKMFo3iWmOUkshUMgKohLAupZIlRH6HjMrDjJSjH1Tl5cAkHUIANrjShEElVhqBbhAE+uTnInyNxiRVikhsbvJCi2mWRXx2KKkv47b4zUhMBklEJdY8ni7jAXN2WKt/AnANJYuBJw6DDJpoCToZC0K1jn5YHD8ghDlSDX8AWsfDXQm+Ajt94dNwJhQ9jPrLzcEGEHiRL1wE6HyqBOkXEak0aRp+v3YChgNPn+ljJmBqQvhwd4coFqAYHpEnhMaGNmxlHUrex+vwD9mt2yR821gVaVQk39lBSB2JhLQBIFzQeDm0Jq9DB77cjdhiY92hx5DGksy6Gj7P1/xBWFX/m9/wAGZnIMtgrsAe+QsBXkdR/OPL2yAM7iFDJ5YleVfkP2iwUaC8rwmRtHIsfo8ln+xXEm0Z/kGj8nRLON2ikgQsit4uyGScxJJhusY0O61CgxAlhrL96EiKTEy/C2nBIdIxELn4d6SEkCQGBHYYHlDaAVRIQQHl6fDmgm+rAKaFbjE4HDxxssrrJ6E4uShMAFJR8Z0tQMgWFLLQ9mP+wl0qLJojvEBSV5DpAXwtzj+Fh2OqGCRLGQ/fIYLZFxb5/9b//Z
"""
# Create the main window
root = tk.Tk()
root.title("mVizn VA Sim")
root.configure(bg='black')

# Define a function that will be called when the "Launch Videos" button is clicked
def hncds_test_click():
    # First command sequence
    hncds_command1 = 'gnome-terminal --title=HNCDS1'
    hncds_cd1 = 'cd ~/Code/mviznARMG/HNCDS/sample/'
    open_hncds1 = 'ffplay -loop 0 2.mp4'
    final_command1 = f"{hncds_command1} -- bash -c '{hncds_cd1} && {open_hncds1}; bash'"

    # Second command sequence
    hncds_command2 = 'gnome-terminal --title=HNCDS2'
    hncds_cd2 = 'cd ~/Code/mviznARMG/HNCDS/sample/'
    open_hncds2 = 'ffplay -loop 0 1.mp4'
    final_command2 = f"{hncds_command2} -- bash -c '{hncds_cd2} && {open_hncds2}; bash'"

    hncds_command3 = 'gnome-terminal --title=HNCDS3'
    hncds_cd3 = 'cd ~/Code/mviznARMG/HNCDS/'
    open_hncds3 = 'ffplay -loop 0 cnssbb-03_25.mp4'
    final_command12 = f"{hncds_command3} -- bash -c '{hncds_cd3} && {open_hncds3}; bash'"

    hncds_command4 = 'gnome-terminal --title=HNCDS4'
    hncds_cd4 = 'cd ~/Code/mviznARMG/HNCDS/'
    open_hncds4 = 'ffplay -loop 0 ovss-21_35.mp4'
    final_command13 = f"{hncds_command4} -- bash -c '{hncds_cd4} && {open_hncds4}; bash'"


    hncds_command5 = 'gnome-terminal --title=HNCDS5'
    hncds_cd5 = 'cd ~/Code/mviznARMG/HNCDS/'
    open_hncds5 = 'ffplay -loop 0 ovtrls-09_30.mp4'
    final_command14 = f"{hncds_command5} -- bash -c '{hncds_cd5} && {open_hncds5}; bash'"

    hncds_command6 = 'gnome-terminal --title=HNCDS5'
    hncds_cd6 = 'cd ~/Code/mviznARMG/HNCDS/'
    open_hncds6 = 'ffplay -loop 0 pmnss-20_40.mp4'
    final_command15 = f"{hncds_command6} -- bash -c '{hncds_cd6} && {open_hncds6}; bash'"

    hncds_command7 = 'gnome-terminal --title=HNCDS5'
    hncds_cd7 = 'cd ~/Code/mviznARMG/HNCDS/'
    open_hncds7 = 'ffplay -loop 0 ts4xf-21_05.mp4'
    final_command16 = f"{hncds_command7} -- bash -c '{hncds_cd7} && {open_hncds7}; bash'"

    # Run the final commands using subprocess
    subprocess.run(final_command1, shell=True)
    subprocess.run(final_command2, shell=True)
    subprocess.run(final_command12, shell=True) 
    subprocess.run(final_command13, shell=True) 
    subprocess.run(final_command14, shell=True) 
    subprocess.run(final_command15, shell=True)
    subprocess.run(final_command16, shell=True)    
# Define a function that will be called when the "End Test" button is clicked
def on_end_test_click():
    subprocess.run("killall gnome-terminal-server", shell=True)

# Define a function that will be called when the "Show Stats" button is clicked
def on_show_stats_click():
    # RAM info command
    ram_command = 'gnome-terminal --title=RAMCPUINFO -- bash -c htop'

    # GPU info command
    gpu_command = 'gnome-terminal --title=GPUINFO -- bash -c nvtop'

    # Run the commands using subprocess
    subprocess.run(ram_command, shell=True)
    subprocess.run(gpu_command, shell=True)

def clps_test_click():
    clps_command1 = 'gnome-terminal --title=CLPS1'
    clps_cd1 = 'cd ~/Code/mviznARMG/CLPS/'
    open_clps1 = 'ffplay -loop 0 ts4xb-16_40.mp4'
    final_command3 = f"{clps_command1} -- bash -c '{clps_cd1} && {open_clps1}; bash'"

    clps_command2 = 'gnome-terminal --title=CLPS2'
    clps_cd2 = 'cd ~/Code/mviznARMG/CLPS/'
    open_clps2 = 'ffplay -loop 0 ts4xf-16_40.mp4'
    final_command4 = f"{clps_command2} -- bash -c '{clps_cd2} && {open_clps2}; bash'"

    subprocess.run(final_command3, shell=True)
    subprocess.run(final_command4, shell=True)

def tcds_test_click():
    tcds_command1 = 'gnome-terminal --title=TCDS1'
    tcds_cd1 = 'cd ~/Code/mviznARMG/TCDS'
    open_tcds1 = 'ffplay -loop 0 cnlsbb-10_45.mp4'
    final_command5 = f"{tcds_command1} -- bash -c '{tcds_cd1} && {open_tcds1}; bash'"

    tcds_command2 = 'gnome-terminal --title=TCDS2'
    tcds_cd2 = 'cd ~/Code/mviznARMG/TCDS'
    open_tcds2 = 'ffplay -loop 0 cnlsbc-10_45.mp4'
    final_command6 = f"{tcds_command2} -- bash -c '{tcds_cd2} && {open_tcds2}; bash'"

    tcds_command3 = 'gnome-terminal --title=TCDS3'
    tcds_cd3 = 'cd ~/Code/mviznARMG/TCDS'
    open_tcds3 = 'ffplay -loop 0 cnlsbf-10_45.mp4'
    final_command7 = f"{tcds_command3} -- bash -c '{tcds_cd3} && {open_tcds3}; bash'"

    tcds_command4 = 'gnome-terminal --title=TCDS4'
    tcds_cd4 = 'cd ~/Code/mviznARMG/TCDS'
    open_tcds4 = 'ffplay -loop 0 tl4xb-10_45.mp4'
    final_command8 = f"{tcds_command4} -- bash -c '{tcds_cd4} && {open_tcds4}; bash'"

    tcds_command5 = 'gnome-terminal --title=TCDS5'
    tcds_cd5 = 'cd ~/Code/mviznARMG/TCDS'
    open_tcds5 = 'ffplay -loop 0 tl4xf-10_45.mp4'
    final_command9 = f"{tcds_command5} -- bash -c '{tcds_cd5} && {open_tcds5}; bash'"

    subprocess.run(final_command5, shell=True)
    subprocess.run(final_command6, shell=True)
    subprocess.run(final_command7, shell=True)
    subprocess.run(final_command8, shell=True)
    subprocess.run(final_command9, shell=True)

def pmnrs_test_click():
    pmnrs_command1 = 'gnome-terminal --title=PMNRS1'
    pmnrs_cd1 = 'cd ~/Code/mviznARMG/PMNRS'
    open_pmnrs1 = 'ffplay -loop 0 ovls-01_10.mp4'
    final_command10 = f"{pmnrs_command1} -- bash -c '{pmnrs_cd1} && {open_pmnrs1}; bash'"

    pmnrs_command2 = 'gnome-terminal --title=PMNRS2'
    pmnrs_cd2 = 'cd ~/Code/mviznARMG/PMNRS'
    open_pmnrs2 = 'ffplay -loop 0 pmnls-01_10.mp4'
    final_command11 = f"{pmnrs_command2} -- bash -c '{pmnrs_cd2} && {open_pmnrs2}; bash'"

    subprocess.run(final_command10, shell=True)
    subprocess.run(final_command11, shell=True)

# Embedding the logo using base64
image_data = base64.b64decode(base64_logo)
image = Image.open(io.BytesIO(image_data))
logo_image = ImageTk.PhotoImage(image)

# Create buttons and add them to the window
button_width = 10

hncds_test_button = tk.Button(root, text="HNCDS", command=hncds_test_click, bg='black', fg='white', width=button_width)
hncds_test_button.grid(row=2, column=2, padx=10, pady=10, sticky="nsew")

clps_test_button = tk.Button(root, text="CLPS", command=clps_test_click, bg='black', fg='white', width=button_width)
clps_test_button.grid(row=2, column=3, padx=10, pady=10, sticky="nsew")

tcds_test_button = tk.Button(root, text="TCDS", command=tcds_test_click, bg='black', fg='white', width=button_width)
tcds_test_button.grid(row=1, column=2, padx=10, pady=10, sticky="nsew")

pmnrs_test_button = tk.Button(root, text="PMNRS", command=pmnrs_test_click, bg='black', fg='white', width=button_width)
pmnrs_test_button.grid(row=1, column=3, padx=10, pady=10, sticky="nsew")

show_stats_button = tk.Button(root, text="Show Stats", command=on_show_stats_click, bg='black', fg='white', width=button_width)
show_stats_button.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

end_test_button = tk.Button(root, text="End Test", command=on_end_test_click, bg='black', fg='white', width=button_width)
end_test_button.grid(row=0, column=5, padx=10, pady=10, sticky="nsew")

#stress_test_button = tk.Button(root, text="Stress Test", command=hncds_test_click ,bg='black', fg='white', width=button_width)
#stress_test_button.grid(row=3, columnspan=8, padx=10, pady=10, sticky="nsew")
# Display the logo on the window
logo_label = tk.Label(root, image=logo_image, bg='black')
logo_label.grid(row=0, column=0, columnspan=8, padx=10, pady=10)  # Span across all columns

root.grid_columnconfigure((0, 1, 2, 3), weight=1)
root.grid_rowconfigure((0, 1, 2), weight=1)

# Start the main event loop
root.mainloop()
