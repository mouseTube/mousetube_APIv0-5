# Welcome to the mouseTube documentation

<div style="display: flex; justify-content: center;">
  <img src="/images/logo_mousetube_big.png" alt="Rodent icon" class="icon-medium">
</div>

This documentation covers an introduction, a description of the vocalizations page, and the backend API of the mouseTube project, which is based on Django.

- [Vocalizations](vocalizations.md)
- [API Python](api/python.md)
- [API REST](api/rest.md)

## <img src="https://cdn.jsdelivr.net/npm/@mdi/svg/svg/rodent.svg" alt="Rodent icon" class="icon-small"> What is mouseTube?

Rodents communicate using various sensory modalities:  
**olfaction** (scent marking, glands), **vision** (postures), **touch** (contacts), and **hearing** (vocalizations).  
These vocalizations are mostly emitted in the **ultrasonic range**, beyond human perception  
([Anderson, 1954](https://doi.org/10.1126/science.119.3101.808); [Brudzynski, 2005](https://doi.org/10.1007/s10519-004-0858-3), [Brudsynski, 2021](https://doi.org/10.3390/brainsci11050605); [Portfors, 2007](https://www.metris.nl/media/documents/TypesandFunctionsofUSVinLabRatsandMice.pdf); [Schweinfurth, 2020](https://doi.org/10.7554/eLife.54020)).

Ultrasonic vocalizations (USVs) are produced in various contexts:

- 🐭 Isolated pups during early life  
- 🧑‍🤝‍🧑 Social interactions in juveniles and adults  
- ♂️ Males in presence of females  
- 😰 Situations of stress, reward anticipation, or exploration

These USVs serve as:

- **Markers of motivation** and **social communication**  
  ([Fischer & Hammerschmidt, 2010](https://doi.org/10.1111/j.1601-183X.2010.00610.x);  
  [Schweinfurth, 2020](https://doi.org/10.7554/eLife.54020))

- **Indicators of stress or anxiety susceptibility**  
  ([Brudzynski, 2005](https://doi.org/10.1007/s10519-004-0858-3))

They are routinely measured in **neuropsychiatric research models**  
([Premoli et al., 2023](https://doi.org/10.1111/ejn.15957)).

---

To address this complexity and data requirement, we developed **mouseTube**:  
a database for sharing, archiving, and analyzing rodent USVs, following the  
**FAIR principles**  
([Wilkinson et al., 2016](https://doi.org/10.1038/sdata.2016.18)):

- 🔍 Findable  
- 🔓 Accessible  
- 🔄 Interoperable  
- ♻️ Reusable

---

## <img src="https://cdn.jsdelivr.net/npm/@mdi/svg/svg/newspaper-variant-multiple-outline.svg" alt="newspaper icon" class="icon-small"> MouseTube Publications

- **Torquet N., de Chaumont F., Faure P., Bourgeron T., Ey E.**  
  *mouseTube – a database to collaboratively unravel mouse ultrasonic communication*  
  *F1000Research 2016, 5:2332*  
  [https://doi.org/10.12688/f1000research.9439.1](https://doi.org/10.12688/f1000research.9439.1)

- **Ferhat A. T., Torquet N., Le Sourd A. M., de Chaumont F., Olivo-Marin J. C., Faure P., Bourgeron T., Ey E.**  
  *Recording Mouse Ultrasonic Vocalizations to Evaluate Social Communication*  
  *J. Vis. Exp. (112), e53871*  
  [https://dx.doi.org/10.3791/53871](https://dx.doi.org/10.3791/53871)

---

## <img src="https://cdn.jsdelivr.net/npm/@mdi/svg/svg/mastodon.svg" alt="mastodon" class="icon-small"> Follow mouseTube on Mastodon

👉 [**@mousetube on Mastodon**](https://mastodon.social/@mousetube)